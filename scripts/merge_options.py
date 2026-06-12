import csv
import json
import os

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"
csv.field_size_limit(10000000)

translations = {}
# Load all 56 chunks
for i in range(56):
    chunk_path = fr".\options_chunk_{i}_ja.json"
    if os.path.exists(chunk_path):
        print(f"Loading chunk {i}...")
        try:
            with open(chunk_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for row_idx_str, text in data.items():
                    translations[int(row_idx_str)] = text
        except Exception as e:
            print(f"Error in chunk {i}: {e}")

print(f"Loaded {len(translations)} translated options.")

rows_to_write = []
updated_count = 0

with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    header_fields = reader.fieldnames
    for row_idx, row in enumerate(reader):
        if row_idx in translations:
            row['options'] = translations[row_idx]
            updated_count += 1
        rows_to_write.append(row)

# Write back
with open(rules_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=header_fields)
    writer.writeheader()
    for row in rows_to_write:
        writer.writerow(row)

print(f"Successfully updated {updated_count} options in rules.csv.")
