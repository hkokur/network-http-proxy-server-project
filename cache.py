import os
from collections import OrderedDict
from threading import Lock

class Cache:
    def __init__(self, cache_dir, max_size):
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = Lock()

        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        else:
            self.clear()

    def _get_cache_path(self, key):
        return os.path.join(self.cache_dir, key.replace("/", "_"))

    def exists(self, key):
        with self.lock:
            return key in self.cache

    def get(self, key):
        with self.lock:
            if key in self.cache:
                # Move the accessed item to the end (LRU behavior)
                self.cache.move_to_end(key)
                cache_path = self._get_cache_path(key)
                with open(cache_path, "rb") as f:
                    return f.read()
        return None

    def put(self, key, value):
        with self.lock:
            # If the key already exists, move it to the end
            if key in self.cache:
                self.cache.move_to_end(key)
            elif len(self.cache) >= self.max_size:
                # Remove the oldest item if the cache is full
                oldest_key, _ = self.cache.popitem(last=False)
                os.remove(self._get_cache_path(oldest_key))

            # Add the new key-value pair to the cache
            self.cache[key] = True
            cache_path = self._get_cache_path(key)
            with open(cache_path, "wb") as f:
                f.write(value)

    def clear(self):
        with self.lock:
            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing cache file {file_path}: {e}")
            self.cache.clear()