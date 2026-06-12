import sys
import os
import config
import os
import csv
import json
import shutil
import math

core_dir = config.APPLICATION_CORE_DIR
plugin_dir = r".\plugins\JP_Lang_Pack\data"

files_to_copy = [
    r"characters\skills\aptitude_data.csv",
    r"characters\skills\skill_data.csv",
    r"shipsystems\ship_systems.csv",
    r"weapons\weapon_data.csv",
    r"world\groups\groups.csv"
]

# Map file -> columns to translate
columns_map = {
    r"characters\skills\aptitude_data.csv": ["name", "desc"],
    r"characters\skills\skill_data.csv": ["name", "desc"],
    r"shipsystems\ship_systems.csv": ["name"],
    r"weapons\weapon_data.csv": ["name", "primaryRoleStr"],
    r"world\groups\groups.csv": ["displayName", "displayNameWithArticle", "displayNameLong", "displayNameLongWithArticle", "personNamePrefix", "shipNamePrefix"]
}

# 1. Copy files
for f in files_to_copy:
    src = os.path.join(core_dir, f)
    dst = os.path.join(plugin_dir, f)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    if not os.path.exists(dst):
        shutil.copy2(src, dst)

# 2. Extract texts
texts_to_translate = {}

for f in files_to_copy:
    dst = os.path.join(plugin_dir, f)
    cols = columns_map[f]
    with open(dst, 'r', encoding='utf-8', errors='ignore') as file:
        reader = csv.DictReader(file)
        # ID column is usually 'id'
        id_col = reader.fieldnames[0] if 'id' not in reader.fieldnames else 'id'
        
        for row in reader:
            row_id = row[id_col]
            if not row_id: continue
            for col in cols:
                if col in row and row[col].strip():
                    key = f"{f}|{row_id}|{col}"
                    texts_to_translate[key] = row[col]

items = list(texts_to_translate.items())
print(f"Total extracted strings: {len(items)}")

# 3. Chunk into 2 files
chunk_size = math.ceil(len(items) / 2)
chunk1 = dict(items[:chunk_size])
chunk2 = dict(items[chunk_size:])

with open(r".\phase3_chunk_1.json", 'w', encoding='utf-8') as f:
    json.dump(chunk1, f, indent=4, ensure_ascii=False)

with open(r".\phase3_chunk_2.json", 'w', encoding='utf-8') as f:
    json.dump(chunk2, f, indent=4, ensure_ascii=False)

print(f"Created phase3_chunk_1.json with {len(chunk1)} items")
print(f"Created phase3_chunk_2.json with {len(chunk2)} items")
