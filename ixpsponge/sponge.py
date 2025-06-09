

class Sponge:

    def __init__(self, mac_address):
        self._mac_address = mac_address
        self._addresses = []

    def add(self, address):
        if address not in self._addresses:
            self._addresses.append(address)

    def remove(self, address):
        if address in self._addresses:
            self._addresses.remove(address)

    def sweep(self, interval):
        for address in self._addresses:
            # ARP reply for address

