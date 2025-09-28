import importlib, time

def test_cache_with_expiry_reference():
    mod = importlib.import_module("tasks.reference.cache_with_expiry")
    Cache = mod.ExpiringCache
    c = Cache(ttl_seconds=1)
    assert c.get("k") is None
    c.put("k", "v")
    assert c.get("k") == "v"
    time.sleep(1.1)  # allow to expire
    assert c.get("k") is None
    # reinsertion works
    c.put("k", "v2")
    assert c.get("k") == "v2"
