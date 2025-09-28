import importlib

def test_log_file_parser_reference():
    mod = importlib.import_module("tasks.reference.log_file_parser")
    parse = mod.parse_errors
    lines = [
        "[t] INFO start",
        "[t] ERROR E123: bad",
        "2025-01-01T00:00:00Z ERROR E123 repeated",
        "[t] WARN minor",
        "[t] ERROR E42: minor",
        "no level here",
        "2025-01-01T00:00:00Z ERROR E999 Disk full",
        "[t] ERROR : missing code",
    ]
    out = parse(lines)
    assert out["E123"] == ["[t] ERROR E123: bad", "2025-01-01T00:00:00Z ERROR E123 repeated"]
    assert out["E42"] == ["[t] ERROR E42: minor"]
    assert out["E999"] == ["2025-01-01T00:00:00Z ERROR E999 Disk full"]
    # missing code shouldn't create empty key
    assert "E" not in out
