from typing import Optional
import time

class ExpiringCache:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self.cache = {}

    def get(self, key: str) -> Optional[str]:
        current_time = time.time()
        if key in self.cache:
            entry = self.cache[key]
            if entry['expiry'] > current_time:
                return entry['value']
            else:
                del self.cache[key]  # Lazily delete expired entries
        return None

    def put(self, key: str, value: str) -> None:
        current_time = time.time()
        expiry_time = current_time + self.ttl_seconds
        self.cache[key] = {'value': value, 'expiry': expiry_time}