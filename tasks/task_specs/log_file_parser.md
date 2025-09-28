# Task: log_file_parser

## Signature
```python
def parse_errors(log_lines: list[str]) -> dict[str, list[str]]:
```

## Description
You are given application log lines (already split by line). Each error line will be in the form:
```
[2025-01-01 12:34:56] ERROR E123: Something bad happened
```
or
```
2025-01-01T12:34:56Z ERROR E999 Disk full
```
Non-error lines may include INFO, WARN, DEBUG, etc.

Write `parse_errors` to return a dictionary mapping **error code** (e.g., `"E123"`) to a list of the **full original lines** that contain that error code, preserving input order within each list.

## Constraints
- Must be a single pass over the input (`O(n)`), where n = number of lines.
- Avoid unnecessary allocations and multiple regex passes. Prefer simple string checks/splits.
- Memory efficient: do not copy the full `log_lines` list; only store needed references/strings.
- Do not print or read input from stdin.

## Edge cases
- Lines with "ERROR" but missing an error code should be ignored.
- Mixed timestamp formats should be accepted.
- Whitespace and trailing spaces may appear.

## Examples
Input:
```
[time] INFO start
[time] ERROR E123: bad
[time] WARN w
2025-01-01T00:00:00Z ERROR E123 repeated
[time] ERROR E42: minor
```

Output (order preserved per code):
```
{
  "E123": ["[time] ERROR E123: bad", "2025-01-01T00:00:00Z ERROR E123 repeated"],
  "E42": ["[time] ERROR E42: minor"]
}
```
