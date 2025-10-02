import time
from typing import Optional, Dict

class ExpiringCache:
    def __init__(self, ttl_seconds: int):
        self.ttl = ttl_seconds
        self.cache: Dict[str, (float, str)] = {}  # key -> (expiry time, value)

    def get(self, key: str) -> Optional[str]:
        """Return the value for a given key if it exists and is not expired."""
        item = self.cache.get(key)
        if item is None or item[0] < time.time():  # If no such key or it's expired
            return None
        else:
            return item[1]

    def put(self, key: str, value: str) -> None:
        """Store a given value for a given key and set its TTL."""
        self.cache[key] = (time.time() + self.ttl, value)