def run_task(log_lines: list[str]) -> dict[str, list[str]]:
    """
    Parses log lines and returns a dictionary mapping error codes to lists of original lines.
    
    Complexity: O(n) time, O(n) space (where n is the number of lines in the input).
    """
    result = {}  # type: dict[str, list[str]]

    for line in log_lines:
        if "ERROR " not in line:
            continue
        
        after_error = line.split("ERROR ", 1)[1].lstrip()
        code = ""
        
        for char in after_error:
            if not (char.isalnum() or char == "_"):
                break
            
            code += char
        
        if code and code[0] == "E":
            result.setdefault(code, []).append(line)
    
    return result