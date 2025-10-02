def normalize_records(data):
    result = []
    for record in data:
        if 'items' not in record or len(record['items']) == 0:
            continue
        user = record.get('user', {})
        user_id = user.get('id')
        user_name = user.get('name')
        for item in record['items']:
            result.append({
                'record_id': record['id'],
                'timestamp': record['timestamp'],
                'user_id': user_id if user_id else None,
                'user_name': user_name if user_name else None,
                'sku': item['sku'],
                'qty': item['qty']
            })
    return result