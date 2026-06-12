import csv
import json
import math
import re

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"
csv.field_size_limit(10000000)

options_to_translate = {}

with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row_idx, row in enumerate(reader):
        if 'options' in row and row['options']:
            text = row['options'].strip()
            # Check if there's any actual English words that need translation
            if re.search(r'[a-zA-Z]{3,}', text) and 'DEV' not in text and 'TODO' not in text:
                options_to_translate[row_idx] = text

items = list(options_to_translate.items())
print(f"Total options extracted: {len(items)}")

chunk_size = 100 # Good size for context
num_chunks = math.ceil(len(items) / chunk_size)

for i in range(num_chunks):
    chunk = dict(items[i*chunk_size : (i+1)*chunk_size])
    with open(fr".\options_chunk_{i}.json", 'w', encoding='utf-8') as f:
        json.dump(chunk, f, indent=4, ensure_ascii=False)

print(f"Created {num_chunks} chunks.")
