import os
import csv
import json
import re

plugin_dir = r'.\plugins\JP_Lang_Pack'

def extract_texts_from_json(data, path_str=""):
    texts = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                texts.append((path_str + f"['{k}']", v))
            else:
                texts.extend(extract_texts_from_json(v, path_str + f"['{k}']"))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, str):
                texts.append((path_str + f"[{i}]", item))
            else:
                texts.extend(extract_texts_from_json(item, path_str + f"[{i}]"))
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
                        # check all text-like columns PLUS the "options" column
                        for col_idx, col_name in enumerate(header):
                            if col_name in ['text', 'desc', 'name', 'tooltip', 'designation', 'description', 'options', 'text1', 'text2', 'title', 'post', 'rank'] and col_idx < len(row):
                                text = row[col_idx]
                                if not text: continue
                                words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
                                valid_words = [w for w in words if '$' not in text and w.lower() not in ['the', 'and', 'for', 'you', 'are', 'not', 'that', 'with', 'this']]
                                if valid_words and 'DEV' not in text and '(dev' not in text.lower():
                                    items_to_translate.append({
                                        'file': path,
                                        'type': 'csv',
                                        'row_idx': i + 1,
                                        'col_name': col_name,
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

with open(r'.\all_untranslated.json', 'w', encoding='utf-8') as f:
    json.dump(items_to_translate, f, ensure_ascii=False, indent=2)

print(f"Total untranslated items saved to all_untranslated.json")
