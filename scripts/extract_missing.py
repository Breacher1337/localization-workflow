import sys
import os
import config
import os
import csv
import json

plugin_dir = r".\plugins\JP_Lang_Pack\data"
core_dir = config.APPLICATION_CORE_DIR

files = [
    r"campaign\compluginities.csv",
    r"campaign\industries.csv",
    r"campaign\market_conditions.csv"
]

translatable_cols = {'name', 'desc'}
extracted = {}

for rel_path in files:
    core_path = os.path.join(core_dir, rel_path)
    with open(core_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for col in translatable_cols:
                if col in row and row[col].strip():
                    key = f"{rel_path}|{row['id']}|{col}"
                    extracted[key] = row[col]

out_path = r".\missing_translations.json"
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(extracted, f, indent=4, ensure_ascii=False)

print(f"Extracted {len(extracted)} strings to missing_translations.json")
