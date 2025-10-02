def run_task(log_lines: list[str]) -> dict[str, list[str]]:
    result = {}
    
    for line in log_lines:
        if "ERROR" not in line:  # Skip lines without ERROR
            continue
            
        error_code = ""
        
        after_error = line.split("ERROR ", 1)[1].lstrip()  # Extract the part after ERROR
        
        for char in after_error:  # Build the error code character by character
            if not (char.isalnum() or char == "_"):  
                break
                
            error_code += char
            
        if error_code and error_code[0] == "E":  # Check if valid error code was extracted
            result.setdefault(error_code, []).append(line)  # Store the result
    
    return result