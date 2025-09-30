from typing import Optional
import time

class ExpiringCache:
    def __init__(self, ttl_seconds: int):
        self.cache = {}  # Dictionary to store key-value pairs
        self.ttl = ttl_seconds  # Time to live for each entry in seconds

    def get(self, key: str) -> Optional[str]:
        if key not in self.cache or time.time() > self.cache[key][1]:
            return None  # If the key does not exist or the value has expired, return None
        else:
            return self.cache[key][0]  # Return the value of the key if it exists and is not expired

    def put(self, key: str, value: str) -> None:
        expiry_time = time.time() + self.ttl  # Calculate the expiry time for this entry
        self.cache[key] = (value, expiry_time)  # Store the value and its expiry time in the cache