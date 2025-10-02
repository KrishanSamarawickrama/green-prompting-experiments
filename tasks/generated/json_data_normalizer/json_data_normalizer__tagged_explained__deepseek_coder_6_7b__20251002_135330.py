def normalize_records(data):
    """
    Normalizes a list of nested JSON-like dictionaries into a flat list of records.
    
    Time complexity: O(n), where n is the number of items in data. We perform a single pass over the input data.
    Space complexity: O(1) as we only use a constant amount of additional space to store the output and intermediate variables.
    """
    result = []  # Initialize an empty list to hold the normalized records
    
    for record in data:  # Iterate over each record in the input data
        if 'items' not in record or len(record['items']) == 0:  
            continue  # If no items, skip this record and move on to next
        
        record_id = record.get('id')  # Get the id of the current record
        timestamp = record.get('timestamp')  # Get the timestamp of the current record
        
        user = record.get('user', {})  # Get the 'user' field, default to empty dict if missing
        user_id = user.get('id')  # Get the id of the user
        user_name = user.get('name')  # Get the name of the user
        
        for item in record['items']:  # Iterate over each item in the current record's items
            sku = item.get('sku')  # Get the sku of the current item
            qty = item.get('qty')  # Get the quantity of the current item
            
            result.append({  # Append a new dictionary to the results list for each item
                'record_id': record_id,
                'timestamp': timestamp,
                'user_id': user_id if user_id else None,
                'user_name': user_name if user_name else None,
                'sku': sku,
                'qty': qty
            })
    
    return result  # Return the list of normalized records