import threading
import toml


class TConfig:

    def __init__(self, filename):
        self._filename = filename
        self._config = toml.load(filename, _dict=dict)
        self._lock = threading.Lock()

    @property
    def lock(self):
        return self._lock

    def reload(self):
        with self._lock:
            self._config = toml.load(self._filename, _dict=dict)

    def get(self, module, key):
        if self._config.get(module):
            return self._config.get(module).get(key)
        else:
            return None
