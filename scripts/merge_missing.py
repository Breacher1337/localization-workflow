import os
import json
import csv

plugin_dir = r".\plugins\JP_Lang_Pack\data"
translations_file = r".\missing_translations_ja.json"

with open(translations_file, 'r', encoding='utf-8') as f:
    translations = json.load(f)

print(f"Loaded {len(translations)} translations.")

files = [
    r"campaign\compluginities.csv",
    r"campaign\industries.csv",
    r"campaign\market_conditions.csv"
]

translatable_cols = {'name', 'desc'}

for rel_path in files:
    plugin_path = os.path.join(plugin_dir, rel_path)
    if not os.path.exists(plugin_path):
        print(f"File not found: {plugin_path}")
        continue
        
    rows_to_write = []
    merged_count = 0
    with open(plugin_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            row_id = row.get('id', '')
            for col in translatable_cols:
                if col in row:
                    key = f"{rel_path}|{row_id}|{col}"
                    if key in translations:
                        row[col] = translations[key]
                        merged_count += 1
            rows_to_write.append(row)
            
    with open(plugin_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator='\r\n')
        writer.writeheader()
        writer.writerows(rows_to_write)
        
    print(f"Merged {merged_count} strings into {rel_path}")

print("Merge complete!")
