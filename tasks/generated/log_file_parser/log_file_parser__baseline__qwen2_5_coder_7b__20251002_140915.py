def run_task(log_lines: list[str]) -> dict[str, list[str]]:
    result = {}
    
    for line in log_lines:
        if " ERROR " not in line:
            continue
        
        parts = line.split("ERROR ", 1)
        after_error = parts[1].lstrip()
        
        code = ""
        for char in after_error:
            if char.isalnum() or char == "_":
                code += char
            else:
                break
        
        if code.startswith("E") and code:
            result.setdefault(code, []).append(line)
    
    return result