from threading import Thread
from .tconfig import TConfig
import json


class TSponge(Thread):

    def __init__(self, config: TConfig):
        Thread.__init__(self)
        self._config = config
        self._sponged_addresses = []
        self._reserved_addresses = []
        self._running = False

    @property
    def config(self) -> TConfig:
        return self._config

    @property
    def sponged_addresses(self) -> list:
        return self._sponged_addresses

    @property
    def reserved_addresses(self) -> list:
        return self._reserved_addresses

    @property
    def running(self) -> bool:
        return self._running

    def reload_reserved_addresses(self):
        self._reserved_addresses.clear()
        filename = self.config.get('general', 'reserved_addresses')
        with open(filename, 'r') as file:
            data = json.load(file)
            self._reserved_addresses.extend(data['addresses'])

    def init_sponged_addresses(self):
        self.reload_reserved_addresses()
        self._sponged_addresses.clear()
        filename = self.config.get('general', 'initial_addresses')

        with open(filename, 'r') as f:
            data = json.load(f)

        for address in data['addresses']:
            if address not in self._reserved_addresses:
                self._sponged_addresses.append(address)

    def reload_sponged_addresses(self):
        self.reload_reserved_addresses()
        self._sponged_addresses.clear()
        filename = self.config.get('general', 'sponged_addresses')

        with open(filename, 'r') as f:
            data = json.load(f)

        for address in data['addresses']:
            if address not in self._reserved_addresses:
                self._sponged_addresses.append(address)

    def sync_sponged_addresses(self):
        filename = self.config.get('general', 'sponged_addresses')
        with open(filename, 'w') as f:
            json.dump(self._sponged_addresses, f)

    def run(self):
        self._running = True

    def halt(self):
        self._running = False



