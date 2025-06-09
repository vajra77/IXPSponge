from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import sendp, sniff
from scapy.arch import get_if_hwaddr
from time import sleep
import getopt
import sys


SNIFF_CACHE = {}
SPONGED_ADDRESSES = []


def arp_account(packet):
    if ARP in packet and packet[ARP].op == 1: #who-has or is-at
        src_addr = packet[ARP].psrc
        if src_addr in SNIFF_CACHE.keys():
            SNIFF_CACHE[src_addr] += 1
        else:
            SNIFF_CACHE[src_addr] = 1


def arp_sweep(interface, addresses, interval):
    src_mac = get_if_hwaddr(interface)
    for ip_address in addresses:
        reply = ARP(op=ARP.is_at, hwsrc=src_mac, psrc=ip_address, hwdst="ff:ff:ff:ff:ff:ff", pdst=ip_address)
        frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=src_mac) / reply
        sendp(frame, iface=interface)
        sleep(interval)


def arp_monitor(interface, count, threshold):
        sniff(iface=interface, filter="arp", prn=arp_account, count=count)
        for address in SNIFF_CACHE.keys():
            if SNIFF_CACHE[address] > threshold:
                add_sponged_addres(address)
        SNIFF_CACHE.clear()


def add_sponged_addres(address):
    if address not in SPONGED_ADDRESSES:
        SPONGED_ADDRESSES.append(address)


def del_sponged_address(address):
    if address in SPONGED_ADDRESSES:
        SPONGED_ADDRESSES.remove(address)



if __name__ == "__main__":

    interface = None

    opts, args = getopt.getopt(sys.argv[1:], "i:", ["iface="])

    for opt, arg in opts:
        if opt == "--iface":
            interface = arg
        else:
            assert False, "unhandled option"

