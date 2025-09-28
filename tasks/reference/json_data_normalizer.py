"""
Flatten nested JSON-like dicts into row records without extra passes.
"""
from typing import List, Dict, Any

def normalize_records(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    append = out.append  # bind locally for speed
    for rec in data:
        rid = rec.get("id")
        ts = rec.get("timestamp")
        user = rec.get("user") or {}
        uid = user.get("id")
        uname = user.get("name")
        items = rec.get("items") or []
        if not items:
            continue
        for it in items:
            append({
                "record_id": rid,
                "timestamp": ts,
                "user_id": uid,
                "user_name": uname,
                "sku": it.get("sku"),
                "qty": it.get("qty"),
            })
    return out
