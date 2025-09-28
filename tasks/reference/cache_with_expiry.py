"""
Simple in-memory expiring cache.
get/put average O(1). Lazy removal on access.
"""
import time
from typing import Optional, Dict, Tuple

class ExpiringCache:
    def __init__(self, ttl_seconds: int):
        if ttl_seconds <= 0:
            raise ValueError("ttl_seconds must be positive")
        self._ttl = ttl_seconds
        # key -> (value, expires_at)
        self._store: Dict[str, Tuple[str, float]] = {}

    def get(self, key: str) -> Optional[str]:
        item = self._store.get(key)
        if not item:
            return None
        value, exp = item
        now = time.time()
        if now >= exp:
            # expired: lazily delete
            self._store.pop(key, None)
            return None
        return value

    def put(self, key: str, value: str) -> None:
        exp = time.time() + self._ttl
        self._store[key] = (value, exp)
