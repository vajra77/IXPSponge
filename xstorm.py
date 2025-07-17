import sys
import getopt
import random
import struct
import socket
from scapy.layers.l2 import ARP, Ether
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr, get_if_addr
#from scapy.arch.unix import get_if_raw_hwaddr


def usage():
    print("Usage: xstorm.py -i <interface> -t [arp|dhcp]")


def run_arp(iface):
    src_addr = get_if_addr(iface)
    src_mac = get_if_hwaddr(iface)
    while True:
        address = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        # request = ARP(op=2, hwsrc=src_mac, psrc=src_addr, hwdst="ff:ff:ff:ff:ff:ff", pdst=address)
        request = ARP(pdst=address, psrc=src_addr)
        frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=src_mac) / request
        sendp(frame, iface=iface)


def run_dhcp(iface):
    src_addr = get_if_addr(iface)
    src_mac = get_if_hwaddr(iface)
    while True:
        ethernet = Ether(dst='ff:ff:ff:ff:ff:ff', src=src_mac, type=0x800)
        ip = IP(src=src_addr, dst='255.255.255.255')
        udp = UDP(sport=68, dport=67)
        # fam, hw = get_if_raw_hwaddr(interface)
        bootp = BOOTP(chaddr=src_mac, ciaddr='0.0.0.0', xid=0x01020304, flags=1)
        dhcp = DHCP(options=[("message-type", "discover"), "end"])
        frame = ethernet / ip / udp / bootp / dhcp
        sendp(frame, iface=iface)


if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "i:t:", ["interface=", "type="])
    except getopt.GetoptError as err:
        print(err)  # will print something like "option -a not recognized"
        usage()
        sys.exit(2)

    interface = None
    pkt_type = None

    for o, a in opts:
        if o in ("-i", "--interface"):
            interface = a
        elif o in ("-t", "--type"):
            pkt_type = a
        else:
            assert False, "unhandled option"

    if pkt_type == "arp":
        run_arp(interface)
    elif pkt_type == "dhcp":
        run_dhcp(interface)
    else:
        assert False, "unhandled packet type"

