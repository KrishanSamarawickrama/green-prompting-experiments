def normalize_records(data):
    """Normalizes a list of nested JSON-like dictionaries into a flat list of records."""
    
    # Initialize an empty list to store the normalized data.
    normalized_data = []

    for record in data:
        if 'items' not in record or len(record['items']) == 0:
            continue  # Skip this record if there are no items.
        
        user = record.get('user', {})  # Get the user dictionary, default to empty if missing.
        user_id = user.get('id')  # Get the user id, None if missing.
        user_name = user.get('name')  # Get the user name, None if missing.
        
        for item in record['items']:
            normalized_data.append({
                'record_id': record['id'],
                'timestamp': record['timestamp'],
                'user_id': user_id,
                'user_name': user_name,
                'sku': item['sku'],
                'qty': item['qty']
            })
    
    return normalized_data