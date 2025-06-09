import lockfile
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import sendp, sniff
from scapy.arch import get_if_hwaddr
from time import sleep
import daemon
import signal
import syslog
import json
import toml
import getopt
import sys


SNIFF_CACHE = {}
SPONGED_ADDRESSES = []
RESERVED_ADDRESSES = []
RUNNING = True


def sig_shutdown(signum, frame):
    global RUNNING

    RUNNING = False
    syslog.syslog(syslog.LOG_INFO, f"Shutdown signal received, saving sponge addresses to {CONFIG['backend']['running']}")
    save_sponged_addresses(CONFIG['backend']['running'])
    exit(0)


def arp_account(packet):
    global SNIFF_CACHE

    if ARP in packet and packet[ARP].op == 1: #who-has or is-at
        src_addr = packet[ARP].psrc
        if src_addr in SNIFF_CACHE.keys():
            SNIFF_CACHE[src_addr] += 1
        else:
            SNIFF_CACHE[src_addr] = 1


def arp_sweep(interface, interval):
    src_mac = get_if_hwaddr(interface)
    for ip_address in SPONGED_ADDRESSES:
        reply = ARP(op=ARP.is_at, hwsrc=src_mac, psrc=ip_address, hwdst="ff:ff:ff:ff:ff:ff", pdst=ip_address)
        frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=src_mac) / reply
        sendp(frame, iface=interface)
        sleep(interval)


def arp_monitor(interface, count, threshold):
    global SNIFF_CACHE

    sniff(iface=interface, filter="arp", prn=arp_account, count=count)
    for address in SNIFF_CACHE.keys():
        if SNIFF_CACHE[address] > threshold:
            if address in RESERVED_ADDRESSES:
                syslog.syslog(syslog.LOG_WARNING, f"Attempt to sponge reserved address [{address}], skipping.")
            else:
                syslog.syslog(syslog.LOG_INFO,
                              f"Adding [{address}] to sponge: {SNIFF_CACHE[address]}/{threshold}")
                add_sponged_address(address)
    SNIFF_CACHE.clear()


def add_sponged_address(address):
    global SPONGED_ADDRESSES

    if address not in SPONGED_ADDRESSES:
        SPONGED_ADDRESSES.append(address)


def del_sponged_address(address):
    global SPONGED_ADDRESSES

    if address in SPONGED_ADDRESSES:
        SPONGED_ADDRESSES.remove(address)


def load_sponged_addresses(filename):
    global SPONGED_ADDRESSES

    SPONGED_ADDRESSES.clear()
    with open(filename, 'r') as file:
        data = json.load(file)
        for address in data['addresses']:
            if address in RESERVED_ADDRESSES:
                syslog.syslog(syslog.LOG_WARNING, f"Attempt to load reserved address [{address}], skipping.")
            else:
                SPONGED_ADDRESSES.append(address)


def load_reserved_addresses(filename):
    global RESERVED_ADDRESSES

    RESERVED_ADDRESSES.clear()
    with open(filename, 'r') as file:
        data = json.load(file)
        RESERVED_ADDRESSES.extend(data['addresses'])


def save_sponged_addresses(filename):
    with open(filename, 'w') as f:
        data = {'addresses': SPONGED_ADDRESSES}
        json.dump(data, f, indent=4) # noqa


def usage():
    print("Usage: xsponge -c <path_to_config_file>")


def main():

    global RUNNING

    load_reserved_addresses(CONFIG['backend']['reserved'])

    if CONFIG['sponge']['preload']:
        load_sponged_addresses(CONFIG['backend']['initial'])

    while RUNNING:
        try:
            if CONFIG['sponge']['enabled']:
                arp_sweep(CONFIG['sponge']['interface'],
                          CONFIG['sponge']['interval'])

            if CONFIG['monitor']['enabled']:
                arp_monitor(CONFIG['monitor']['interface'],
                            CONFIG['monitor']['count'],
                            CONFIG['monitor']['threshold'])
                save_sponged_addresses(CONFIG['backend']['running'])

            sleep(30)

        except KeyboardInterrupt:
            RUNNING = False


if __name__ == "__main__":

    config_file = "assets/xsponge.conf"

    opts, args = getopt.getopt(sys.argv[1:], "hc:", ["help", "config="])

    for opt, arg in opts:
        if opt == "--config":
            config_file = arg
        elif opt == "--help":
            usage()
            exit(0)
        else:
            print("Unhandled option %s" % opt, file=sys.stderr)
            usage()
            exit(1)

    try:
        CONFIG = toml.load(config_file, _dict=dict)
    except FileNotFoundError:
        print("Configuration file not found", file=sys.stderr)
        usage()
        exit(1)

    with daemon.DaemonContext(
            pidfile=lockfile.FileLock(CONFIG['pid_file']),
            signal_map={
                signal.SIGTERM: sig_shutdown,
                signal.SIGTSTP: sig_shutdown,
                signal.SIGHUP: sig_shutdown,
            }):
        main()

