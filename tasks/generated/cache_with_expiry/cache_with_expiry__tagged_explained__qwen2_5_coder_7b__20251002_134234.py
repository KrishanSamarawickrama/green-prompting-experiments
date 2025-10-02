from typing import Optional
import time

class ExpiringCache:
    def __init__(self, ttl_seconds: int):
        self.ttl = ttl_seconds
        self.cache = {}

    def get(self, key: str) -> Optional[str]:
        current_time = time.time()
        if key in self.cache:
            value, expire_at = self.cache[key]
            if expire_at > current_time:
                return value
            else:
                del self.cache[key]
        return None

    def put(self, key: str, value: str) -> None:
        current_time = time.time()
        expire_at = current_time + self.ttl
        self.cache[key] = (value, expire_at)