def run_task(log_lines: list[str]) -> dict[str, list[str]]:
    result = {}
    
    for line in log_lines:
        if "ERROR" not in line:
            continue
            
        error_code = ""
        
        after_error = line.split("ERROR ", 1)[1].lstrip()
        for char in after_error:
            if char.isalnum() or char == "_":
                error_code += char
            else:
                break
                
        if error_code and error_code[0] == "E" and len(error_code) > 1:
            result.setdefault(error_code, []).append(line)
            
    return result