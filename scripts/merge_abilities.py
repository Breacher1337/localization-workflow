import csv
import json

plugin_path = r".\plugins\JP_Lang_Pack\data\campaign\abilities.csv"
chunk_path = r".\abilities_chunk_ja.json"

with open(chunk_path, 'r', encoding='utf-8') as f:
    translations = json.load(f)

rows_to_write = []
with open(plugin_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        row_id = row['id']
        if not row_id:
            rows_to_write.append(row)
            continue
        
        # update name
        key_name = f"{row_id}|name"
        if key_name in translations:
            row['name'] = translations[key_name]
            
        # update desc
        key_desc = f"{row_id}|desc"
        if key_desc in translations:
            row['desc'] = translations[key_desc]
            
        rows_to_write.append(row)

with open(plugin_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows_to_write:
        writer.writerow(row)

print("Successfully merged translated abilities back into abilities.csv!")
