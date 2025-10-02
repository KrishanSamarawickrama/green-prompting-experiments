# Task: log_file_parser

## Signature
```python
def run_task(log_lines: list[str]) -> dict[str, list[str]]:
```

## Description
You are given application log lines (already split by line). Each error line contains the word "ERROR" followed by an error code that starts with "E" (like E123, E999, E42).

**Error line formats:**
```
[2025-01-01 12:34:56] ERROR E123: Something bad happened
2025-01-01T12:34:56Z ERROR E999 Disk full
[t] ERROR E42: minor issue
```

**Key parsing rules:**
1. Only process lines containing "ERROR " (with space after)
2. Find the error code that comes after "ERROR " - it must start with "E" followed by alphanumeric characters
3. Error codes are the first token after "ERROR " that starts with "E"
4. Ignore lines where no valid error code can be extracted

Write `run_task` to return a dictionary mapping **error code** (e.g., `"E123"`) to a list of the **full original lines** that contain that error code, preserving input order within each list.

## Algorithm Steps

1. **For each line in log_lines:**
   - Check if line contains "ERROR " (note the space)
   - If not, skip to next line
   
2. **Extract error code:**
   - Split the line around "ERROR " to get the part after it: `line.split("ERROR ", 1)`
   - Take the first token (word) from that part by iterating character by character
   - Stop at first non-alphanumeric character (space, colon, etc.)
   - Check if the extracted token starts with "E" and is non-empty
   - If valid, this is your error code
   
3. **Store the result:**
   - Add the error code as a key in your result dictionary (if not already present)
   - Append the entire original line to the list for that error code

## Implementation Hints

- Use `line.split("ERROR ", 1)` to split only on the first occurrence
- Use `after_error.lstrip()` to remove leading whitespace after "ERROR "
- Build the error code character by character: `char.isalnum() or char == "_"`
- Use dictionary `setdefault()` or check `if code not in dict:` to initialize lists

## Constraints

- Must be a single pass over the input (`O(n)`), where n = number of lines.
- Avoid unnecessary allocations and multiple regex passes. Prefer simple string checks/splits.
- Memory efficient: do not copy the full `log_lines` list; only store needed references/strings.
- Do not print or read input from stdin.

## Edge Cases to Handle

- Lines with "ERROR" but missing an error code should be ignored.
- Lines like `"[t] ERROR : missing code"` should be ignored (no valid error code)
- Mixed timestamp formats should be accepted.
- Whitespace and trailing spaces may appear.
- Error codes may be followed by colons, spaces, or other punctuation.

## Complete Example

Input:

```text
[t] INFO start
[t] ERROR E123: bad
2025-01-01T00:00:00Z ERROR E123 repeated
[t] WARN minor
[t] ERROR E42: minor
no level here
2025-01-01T00:00:00Z ERROR E999 Disk full
[t] ERROR : missing code
```

Expected Output (order preserved per code):

```python
{
  "E123": ["[t] ERROR E123: bad", "2025-01-01T00:00:00Z ERROR E123 repeated"],
  "E42": ["[t] ERROR E42: minor"],
  "E999": ["2025-01-01T00:00:00Z ERROR E999 Disk full"]
}
```

Note: The line `"[t] ERROR : missing code"` is ignored because there's no valid error code after "ERROR ".
