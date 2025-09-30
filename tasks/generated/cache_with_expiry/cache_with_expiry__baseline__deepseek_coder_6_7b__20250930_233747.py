import time
from typing import Optional

class ExpiringCache:
    def __init__(self, ttl_seconds: int):
        self.cache = {}
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[str]:
        if key in self.cache and time.time() - self.cache[key][1] < self.ttl:
            return self.cache[key][0]
        else:
            return None

    def put(self, key: str, value: str) -> None:
        self.cache[key] = (value, time.time())