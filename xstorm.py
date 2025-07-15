import sys
import random
import struct
import socket
from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr, get_if_addr


if __name__ == '__main__':
    interface = sys.argv[1]
    src_addr = get_if_addr(interface)
    src_mac = get_if_hwaddr(interface)

    while True:
        address = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))
        # request = ARP(op=2, hwsrc=src_mac, psrc=src_addr, hwdst="ff:ff:ff:ff:ff:ff", pdst=address)
        request = ARP(pdst=address)
        frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=src_mac) / request
        sendp(frame, iface=interface)
