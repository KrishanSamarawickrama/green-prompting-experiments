def run_task(data):
    result = []
    
    for record in data:
        if 'items' not in record or len(record['items']) == 0:
            continue
            
        user = record.get('user', {})
        
        for item in record['items']:
            row = {}
            row['record_id'] = record['id']
            row['timestamp'] = record['timestamp']
            row['user_id'] = user.get('id') if 'id' in user else None
            row['user_name'] = user.get('name') if 'name' in user else None
            row['sku'] = item['sku']
            row['qty'] = item['qty']
            
            result.append(row)
    
    return result