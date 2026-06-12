import os
import csv
import json
import re
import math

plugin_dir = r'.\plugins\JP_Lang_Pack'

def extract_texts_from_json(data, path_str=""):
    texts = []
    if isinstance(data, dict):
        for k, v in data.items():
            texts.extend(extract_texts_from_json(v, path_str + f"['{k}']"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            texts.extend(extract_texts_from_json(item, path_str + f"[{i}]"))
    elif isinstance(data, str):
        texts.append((path_str, data))
    return texts

items_to_translate = []

for root, dirs, files in os.walk(plugin_dir):
    for f in files:
        path = os.path.join(root, f)
        if f.endswith('.csv'):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    header = next(reader)
                    for i, row in enumerate(reader):
                        for col_idx, col_name in enumerate(header):
                            if col_name in ['text', 'desc', 'name', 'tooltip', 'designation', 'description'] and col_idx < len(row):
                                text = row[col_idx]
                                if not text: continue
                                words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
                                valid_words = [w for w in words if '$' not in text and w.lower() not in ['the', 'and', 'for', 'you', 'are', 'not', 'that', 'with', 'this']]
                                # Ignore DEV strings
                                if valid_words and 'DEV' not in text and '(dev' not in text.lower():
                                    items_to_translate.append({
                                        'file': path,
                                        'type': 'csv',
                                        'row_idx': i + 1, # +1 because of header
                                        'col_idx': col_idx,
                                        'text': text
                                    })
            except Exception as e:
                pass
        elif f.endswith('.json'):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    texts = extract_texts_from_json(data)
                    for json_path, text in texts:
                        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
                        valid_words = [w for w in words if '$' not in text and w.lower() not in ['the', 'and', 'for', 'you', 'are', 'not', 'that', 'with', 'this']]
                        if valid_words and 'DEV' not in text and '(dev' not in text.lower():
                            items_to_translate.append({
                                'file': path,
                                'type': 'json',
                                'json_path': json_path,
                                'text': text
                            })
            except Exception as e:
                pass

print(f"Total items needing translation (excluding DEV): {len(items_to_translate)}")

# Split into 4 chunks
chunk_size = math.ceil(len(items_to_translate) / 4)
for i in range(4):
    chunk = items_to_translate[i*chunk_size : (i+1)*chunk_size]
    with open(f'.\\translation_chunk_{i+1}.json', 'w', encoding='utf-8') as out:
        json.dump(chunk, out, ensure_ascii=False, indent=2)
    print(f"Chunk {i+1}: {len(chunk)} items.")
