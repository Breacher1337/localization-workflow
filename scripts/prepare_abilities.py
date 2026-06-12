import sys
import os
import config
import os
import shutil
import csv
import json

core_path = config.APPLICATION_CORE_DIR
plugin_path = r".\plugins\JP_Lang_Pack\data\campaign\abilities.csv"

# 1. Copy file
os.makedirs(os.path.dirname(plugin_path), exist_ok=True)
shutil.copy2(core_path, plugin_path)
print("Copied abilities.csv to plugin folder.")

# 2. Extract texts to translate (name, desc)
texts_to_translate = {}
with open(plugin_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        row_id = row['id']
        if not row_id: continue
        for col in ['name', 'desc']:
            if col in row and row[col].strip():
                texts_to_translate[f"{row_id}|{col}"] = row[col]

# 3. Save as JSON chunk
chunk_path = r".\abilities_chunk.json"
with open(chunk_path, 'w', encoding='utf-8') as f:
    json.dump(texts_to_translate, f, indent=4, ensure_ascii=False)

print(f"Extracted {len(texts_to_translate)} strings into abilities_chunk.json.")
