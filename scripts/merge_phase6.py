import sys
import os
import config
import os
import json
import csv

plugin_dir = r".\plugins\JP_Lang_Pack\data"
core_dir = config.APPLICATION_CORE_DIR
masterlist_csv = r".\localization_masterlist.csv"

# Load all translated chunks
translations = {}
for i in range(51):
    chunk_path = fr".\phase6_csv_chunk_{i}_ja.json"
    if os.path.exists(chunk_path):
        with open(chunk_path, 'r', encoding='utf-8') as f:
            translations.update(json.load(f))
            
print(f"Loaded {len(translations)} translated strings from chunks.")

translatable_cols = {'name', 'desc', 'text', 'options', 'displayName', 'designation', 'primaryRoleStr', 'personNamePrefix', 'shipNamePrefix', 'text1', 'text2', 'text3', 'text4', 'text5', 'subject', 'summary', 'assessment'}

files_to_merge = []
with open(masterlist_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Type'] == 'CSV' and (row['Status'] != 'Translated (Contains Japanese)' or 'descriptions.csv' in row['File Path']):
            files_to_merge.append(row['File Path'])

for rel_path in files_to_merge:
    core_path = os.path.join(core_dir, rel_path)
    plugin_path = os.path.join(plugin_dir, rel_path)
    
    if not os.path.exists(core_path): continue
    
    os.makedirs(os.path.dirname(plugin_path), exist_ok=True)
    
    # Read core file, replace with translation, write to plugin file
    rows_to_write = []
    with open(core_path, 'r', encoding='utf-8', errors='ignore') as cf:
        reader = csv.DictReader(cf)
        fieldnames = reader.fieldnames
        has_id = 'id' in fieldnames
        row_idx = 0
        for row in reader:
            row_key = row['id'] if has_id else str(row_idx)
            for col in translatable_cols:
                global_key = f"{rel_path}|{row_key}|{col}"
                if global_key in translations:
                    row[col] = translations[global_key]
            rows_to_write.append(row)
            row_idx += 1
            
    with open(plugin_path, 'w', encoding='utf-8', newline='') as mf:
        writer = csv.DictWriter(mf, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows_to_write)
        
    print(f"Merged translations into {rel_path}")

print("Phase 6 CSV merge complete!")
