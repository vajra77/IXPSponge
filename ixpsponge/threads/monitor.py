from scapy.layers.l2 import ARP, Ether
from scapy.sendrecv import sniff
from .tconfig import TConfig
from .tsponge import TSponge
from time import sleep
import syslog


class Monitor(TSponge):

    def __init__(self, config: TConfig):
        super().__init__(config)
        self._cached_addresses = {}

    def handle_packet(self, packet):
        if ARP in packet and packet[ARP].op == 1:  # who-has
            src_addr = packet[ARP].psrc
            if src_addr in self._cached_addresses.keys():
                self._cached_addresses[src_addr] += 1
            else:
                self._cached_addresses[src_addr] = 1


    def run(self):
        super().run()

        threshold = self.config.get('monitor', 'threshold')
        count = int(self.config.get('monitor', 'count'))
        interval = int(self.config.get('monitor', 'interval'))

        while self.running:
            sniff(iface=self.config.get('monitor', 'interface'),
                                        filter="arp",
                                        prn=self.handle_packet,
                                        count=count)

            for address in self._cached_addresses.keys():
                if self._cached_addresses[address] > threshold:
                    if address in self._reserved_addresses:
                        syslog.syslog(syslog.LOG_WARNING, f"Attempt to sponge reserved address [{address}], skipping.")
                    else:
                        syslog.syslog(syslog.LOG_INFO,
                                      f"Adding [{address}] to sponge: {self._cached_addresses[address]}/{threshold}")

                        with self.config.lock:
                            self.reload_sponged_addresses()
                            self._sponged_addresses.append(address)
                            self.sync_sponged_addresses()

            self._cached_addresses.clear()
            sleep(interval)