def run_task(log_lines: list[str]) -> dict[str, list[str]]:
    # Initialize an empty dictionary to store error codes and their corresponding lines
    errors = {}
    
    for line in log_lines:
        if "ERROR" not in line:  # Skip lines without "ERROR"
            continue
            
        after_error, _, _ = line.partition("] ERROR ")  # Split around the first occurrence of "] ERROR "
        
        error_code = ''
        for char in after_error:  # Extract error code character by character
            if not (char.isalnum() or char == '_'):  
                break
                
            error_code += char
            
        if error_code and error_code[0] == 'E':  # Check if the extracted token starts with "E"
            errors.setdefault(error_code, []).append(line)  # Store the result
    
    return errors