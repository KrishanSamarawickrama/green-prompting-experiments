from typing import Optional
import time

class ExpiringCache:
    def __init__(self, ttl_seconds: int):
        self.cache = {}  # type: dict[str, tuple[float, str]]
        self.ttl = ttl_seconds

    def get(self, key: str) -> Optional[str]:
        if key in self.cache:
            creation_time, value = self.cache[key]
            age = time.time() - creation_time
            
            # If the item is not expired, return its value; otherwise delete it and return None
            if age < self.ttl:
                return value
            else:
                del self.cache[key]
        return None

    def put(self, key: str, value: str) -> None:
        # Add the new item to the cache with its creation time
        self.cache[key] = (time.time(), value)