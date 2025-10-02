def normalize_records(data: list[dict]) -> list[dict]:
    result = []
    for record in data:
        user_id = record.get('user', {}).get('id')
        user_name = record.get('user', {}).get('name')
        items = record.get('items', [])
        if not items:
            continue
        for item in items:
            result.append({
                "record_id": record['id'],
                "timestamp": record['timestamp'],
                "user_id": user_id,
                "user_name": user_name,
                "sku": item['sku'],
                "qty": item['qty']
            })
    return result