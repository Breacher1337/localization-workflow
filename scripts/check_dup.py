import csv
with open('descriptions_translated.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    keys = set()
    for i, row in enumerate(reader):
        if not row: continue
        key = row[0] + " | " + row[1] if len(row) > 1 else row[0]
        if key in keys:
            print(f"Duplicate key found at row {i+1}: {key}")
        else:
            keys.add(key)
