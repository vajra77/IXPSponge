from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr
from time import sleep
from .tconfig import TConfig
from .tsponge import TSponge


class Sweeper(TSponge):

    def __init__(self, config: TConfig):
        super().__init__(config)

    def run(self):
        interval = float(self.config.get('sweeper', 'interval'))
        src_mac = get_if_hwaddr(self.config.get('sweeper', 'interface'))

        while True:
            with self.config.lock:
                self.reload_sponged_addresses()

            for address in self.sponged_addresses:
                reply = ARP(op=ARP.is_at, hwsrc=src_mac, psrc=address, hwdst="ff:ff:ff:ff:ff:ff", pdst=address)
                frame = Ether(dst="ff:ff:ff:ff:ff:ff", src=src_mac) / reply
                sendp(frame, iface=self.config.get('sweeper', 'interface'))
                sleep(interval)

            sleep(3 * interval)