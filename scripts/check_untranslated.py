import os
import csv
import json
import re

plugin_dir = r'.\plugins\JP_Lang_Pack'

def contains_japanese(text):
    # Regex matching Hiragana, Katakana, and Kanji
    return bool(re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text))

def extract_texts_from_json(data):
    texts = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                texts.append((k, v))
            else:
                texts.extend([(f"{k}.{sub_k}", sub_v) for sub_k, sub_v in extract_texts_from_json(v)])
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if isinstance(item, str):
                texts.append((str(i), item))
            else:
                texts.extend([(f"{i}.{sub_k}", sub_v) for sub_k, sub_v in extract_texts_from_json(item)])
    return texts

untranslated = []

for root, dirs, files in os.walk(plugin_dir):
    for f in files:
        path = os.path.join(root, f)
        if f.endswith('.csv'):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row_idx, row in enumerate(reader):
                        for col in ['text', 'desc', 'name', 'tooltip', 'designation', 'description']:
                            if col in row and row[col]:
                                text = row[col]
                                # If there's letters but NO Japanese characters
                                if re.search(r'[a-zA-Z]{3,}', text) and not contains_japanese(text):
                                    # Ignore dev strings
                                    if 'DEV' not in text and 'TODO' not in text:
                                        untranslated.append((f, f"Row {row_idx}", text))
            except Exception as e:
                pass
        elif f.endswith('.json'):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    texts = extract_texts_from_json(data)
                    for key, text in texts:
                        if re.search(r'[a-zA-Z]{3,}', text) and not contains_japanese(text):
                            if 'DEV' not in text and 'TODO' not in text:
                                untranslated.append((f, key, text))
            except Exception as e:
                pass

print(f"Found {len(untranslated)} completely untranslated English strings.")
for f, k, t in untranslated[:20]:
    print(f"[{f} | {k}] {t[:50]}...")
