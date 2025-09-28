import importlib

def sort_rows(rows):
    return sorted(rows, key=lambda r: (r["record_id"], r["sku"] or ""))

def test_json_data_normalizer_reference():
    mod = importlib.import_module("tasks.reference.json_data_normalizer")
    norm = mod.normalize_records
    data = [
        {"id": 10, "timestamp": "t1", "user": {"id": 1, "name": "Ann"}, "items": [{"sku": "A", "qty": 2}]},
        {"id": 11, "timestamp": "t2", "items": [{"sku": "B", "qty": 1}, {"sku": "C", "qty": 5}]},
        {"id": 12, "timestamp": "t3", "user": {"id": 2, "name": "Bo"}, "items": []},
        {"id": 13, "timestamp": "t4"},  # no items
    ]
    out = norm(data)
    want = [
        {"record_id":10,"timestamp":"t1","user_id":1,"user_name":"Ann","sku":"A","qty":2},
        {"record_id":11,"timestamp":"t2","user_id":None,"user_name":None,"sku":"B","qty":1},
        {"record_id":11,"timestamp":"t2","user_id":None,"user_name":None,"sku":"C","qty":5},
    ]
    assert sort_rows(out) == sort_rows(want)
