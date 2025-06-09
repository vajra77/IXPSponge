from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr
from time import sleep


class Sponge:

    def __init__(self, interface):
        self._interface = interface
        self._addresses = []

    def add(self, address):
        if address not in self._addresses:
            self._addresses.append(address)

    def remove(self, address):
        if address in self._addresses:
            self._addresses.remove(address)

    def sweep(self, interval):
        src_mac = get_if_hwaddr(self._interface)

        for ip_address in self._addresses:
            reply = ARP(op=ARP.is_at, hwsrc=src_mac, psrc=ip_address, hwdst="ff:ff:ff:ff:ff:ff", pdst=ip_address)
            frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=src_mac) / reply
            sendp(frame, iface=self._interface)
            sleep(interval)

