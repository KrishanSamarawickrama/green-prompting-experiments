# Task: cache_with_expiry

## Signature

```python
from typing import Optional

class ExpiringCache:
    def __init__(self, ttl_seconds: int): ...
    def get(self, key: str) -> Optional[str]: ...
    def put(self, key: str, value: str) -> None: ...
```

## Description

Implement a simple in-memory cache with **time-to-live (TTL)** per entry. When `get` is called, if the item exists and is not expired, return its value; otherwise return `None`.

You will need to import `time` and `Optional` from `typing`.

## Constraints

- Average-case O(1) for `get` and `put` (use a dict; a min-heap is optional).
- TTL is the same for all entries and is set via constructor.
- Use `time.time()` for wall-clock seconds.
- No thread-safety requirements (single-threaded).
- Do not print or read input.

## Notes

- You may lazily delete expired entries on access instead of eagerly scanning.
- Items inserted later have independent expiry times.
