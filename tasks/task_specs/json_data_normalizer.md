# Task: json_data_normalizer

## Signature
```python
def normalize_records(data: list[dict]) -> list[dict]:
```

## Description
Normalize a list of nested JSON-like dictionaries into a **flat** list of records. Each input element may contain:
- top-level fields like `id`, `timestamp`
- a nested object `user` with fields `id`, `name` (may be missing)
- a nested list `items`, where each item has `sku`, `qty`

Return a **flat list** where each item corresponds to a single `(record × item)` row with these keys:
`record_id, timestamp, user_id, user_name, sku, qty`

If `user` is missing, set `user_id` and `user_name` to `None`. If `items` is empty or missing, **return no rows** for that record.

## Constraints
- Single pass over `data` (ignore negligible inner loops over each record's items).
- Avoid building large intermediate structures; append rows directly.
- Be robust to missing keys.

## Example
Input:
```
[
  {"id": 10, "timestamp": "t1", "user": {"id": 1, "name": "Ann"}, "items": [{"sku": "A", "qty": 2}]},
  {"id": 11, "timestamp": "t2", "items": [{"sku": "B", "qty": 1}, {"sku": "C", "qty": 5}]}
]
```
Output:
```
[
  {"record_id":10,"timestamp":"t1","user_id":1,"user_name":"Ann","sku":"A","qty":2},
  {"record_id":11,"timestamp":"t2","user_id":None,"user_name":None,"sku":"B","qty":1},
  {"record_id":11,"timestamp":"t2","user_id":None,"user_name":None,"sku":"C","qty":5}
]
```
