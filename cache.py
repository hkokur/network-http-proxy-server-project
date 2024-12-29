import os
import logging
from collections import OrderedDict
from threading import Lock

class Cache:
    def __init__(self, cache_dir, max_size):
        # Initialize cache directory and maximum size
        self.cache_dir = cache_dir
        self.max_size = max_size
        self.cache = OrderedDict()
        self.lock = Lock()

        # Check if cache directory exists
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)
        else:
            self.clear()  # Clear existing cache directory

    def _get_cache_path(self, key):
        # Replace '/'
        return os.path.join(self.cache_dir, key.replace("/", "_"))

    def exists(self, key):
        with self.lock:
            return key in self.cache

    def get(self, key):
        with self.lock:
            if key in self.cache:
                logging.info(f"Cache hit for key: {key}")
                self.cache.move_to_end(key)  # Mark key as recently used
                cache_path = self._get_cache_path(key)
                with open(cache_path, "rb") as f:
                    return f.read()  # Return cached data
            logging.info(f"Cache miss for key: {key}")
        return None

    def put(self, key, value):
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)  # Mark as recently used
            elif len(self.cache) >= self.max_size:
                oldest_key, _ = self.cache.popitem(last=False)  # Remove least recently used item
                os.remove(self._get_cache_path(oldest_key))  # Delete cache file

            self.cache[key] = True
            cache_path = self._get_cache_path(key)
            with open(cache_path, "wb") as f:
                f.write(value)  # Write value to cache file

    def clear(self):
        with self.lock:
            for filename in os.listdir(self.cache_dir):  # Iterate over cache files
                file_path = os.path.join(self.cache_dir, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error removing cache file {file_path}: {e}")
            self.cache.clear()  # Clear in-memory cache