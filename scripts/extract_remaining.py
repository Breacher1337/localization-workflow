import sys
import os
import config
import os
import csv
import json

plugin_dir = r".\plugins\JP_Lang_Pack\data"
masterlist_csv = r".\localization_masterlist.csv"

# Columns to translate
translatable_cols = {'name', 'desc', 'text', 'options', 'displayName', 'designation', 'primaryRoleStr', 'personNamePrefix', 'shipNamePrefix', 'text1', 'text2', 'text3', 'text4', 'text5', 'subject', 'summary', 'assessment'}

files_to_translate = []
with open(masterlist_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        # We process files that are either NOT in plugin folder, or in Plugin folder but English
        # Wait, if it's "Translated (Contains Japanese)", we might want to skip, UNLESS it's descriptions.csv which is partially translated.
        if row['Status'] != 'Translated (Contains Japanese)' or 'descriptions.csv' in row['File Path']:
            files_to_translate.append(row['File Path'])

print(f"Found {len(files_to_translate)} files to process.")

# Actually, to make things cleaner, let's extract everything from the core directory for these files,
# but skip strings that already have Japanese in the plugin directory version (to save work).

import re
def is_japanese(text):
    return bool(re.search(r'[あ-んア-ン一-龥]', text))

core_dir = config.APPLICATION_CORE_DIR
extracted_data = {}

for rel_path in files_to_translate:
    core_path = os.path.join(core_dir, rel_path)
    plugin_path = os.path.join(plugin_dir, rel_path)
    
    # Pre-load existing plugin file translations if any
    existing_plugin_data = {}
    if os.path.exists(plugin_path):
        if rel_path.endswith('.csv'):
            try:
                with open(plugin_path, 'r', encoding='utf-8', errors='ignore') as mf:
                    mr = csv.DictReader(mf)
                    # We need a unique key. Most CSVs have 'id'
                    if 'id' in mr.fieldnames:
                        for row in mr:
                            row_id = row['id']
                            for col in translatable_cols:
                                if col in row and is_japanese(row[col]):
                                    existing_plugin_data[f"{rel_path}|{row_id}|{col}"] = True
            except: pass
            
    # Now read core file
    if not os.path.exists(core_path):
        continue
        
    if rel_path.endswith('.csv'):
        with open(core_path, 'r', encoding='utf-8', errors='ignore') as cf:
            cr = csv.DictReader(cf)
            if not cr.fieldnames: continue
            has_id = 'id' in cr.fieldnames
            row_idx = 0
            for row in cr:
                row_key = row['id'] if has_id else str(row_idx)
                for col in translatable_cols:
                    if col in row and row[col].strip():
                        global_key = f"{rel_path}|{row_key}|{col}"
                        if global_key not in existing_plugin_data:
                            extracted_data[global_key] = row[col]
                row_idx += 1
    elif rel_path.endswith('.json') or rel_path.endswith('.group'):
        # Just dump the whole file content into the chunk, it's easier for the LLM to just translate the whole JSON
        # Wait, if it's large, we can't. Let's just pass the file paths to the subagent and have it read/write directly.
        pass

# Save extracted CSV data
chunk_size = 100
keys = list(extracted_data.keys())
total_chunks = (len(keys) // chunk_size) + 1

for i in range(total_chunks):
    chunk_keys = keys[i*chunk_size : (i+1)*chunk_size]
    if not chunk_keys: continue
    
    chunk_dict = {k: extracted_data[k] for k in chunk_keys}
    out_path = fr".\phase6_csv_chunk_{i}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(chunk_dict, f, indent=4, ensure_ascii=False)

print(f"Extracted {len(keys)} CSV strings into {total_chunks} chunks.")
