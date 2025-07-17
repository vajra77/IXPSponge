import sys
import random
import struct
import socket
from scapy.layers.l2 import ARP, Ether
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr, get_if_addr
from scapy.arch.unix import get_if_raw_hwaddr


if __name__ == '__main__':
    interface = sys.argv[1]
    src_addr = get_if_addr(interface)
    src_mac = get_if_hwaddr(interface)

    while True:
        address = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        # request = ARP(op=2, hwsrc=src_mac, psrc=src_addr, hwdst="ff:ff:ff:ff:ff:ff", pdst=address)
        # request = ARP(pdst=address, psrc="192.168.204.1")
        # frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=src_mac) / request

        ethernet = Ether(dst='ff:ff:ff:ff:ff:ff', src=src_mac, type=0x800)
        ip = IP(src=src_addr, dst='255.255.255.255')
        udp = UDP(sport=68, dport=67)
        #fam, hw = get_if_raw_hwaddr(interface)
        bootp = BOOTP(chaddr=src_mac, ciaddr='0.0.0.0', xid=0x01020304, flags=1)
        dhcp = DHCP(options=[("message-type", "discover"), "end"])
        frame = ethernet / ip / udp / bootp / dhcp

        sendp(frame, iface=interface)
