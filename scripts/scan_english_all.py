import os
import csv
import json
import re

plugin_dir = r'.\plugins\JP_Lang_Pack'

def extract_texts_from_json(data):
    texts = []
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, str):
                texts.append(v)
            else:
                texts.extend(extract_texts_from_json(v))
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, str):
                texts.append(item)
            else:
                texts.extend(extract_texts_from_json(item))
    return texts

english_sentences = []

for root, dirs, files in os.walk(plugin_dir):
    for f in files:
        path = os.path.join(root, f)
        if f.endswith('.csv'):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        for col in ['text', 'desc', 'name', 'tooltip', 'designation', 'description']:
                            if col in row and row[col]:
                                text = row[col]
                                # Check for english words >= 3 chars not starting with $
                                words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
                                valid_words = [w for w in words if '$' not in text and w.lower() not in ['the', 'and', 'for', 'you', 'are', 'not', 'that', 'with', 'this']]
                                if valid_words:
                                    english_sentences.append((f, text))
            except Exception as e:
                pass
        elif f.endswith('.json'):
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    texts = extract_texts_from_json(data)
                    for text in texts:
                        words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
                        valid_words = [w for w in words if '$' not in text and w.lower() not in ['the', 'and', 'for', 'you', 'are', 'not', 'that', 'with', 'this']]
                        if valid_words:
                            english_sentences.append((f, text))
            except Exception as e:
                pass

with open(r'.\remaining_english.txt', 'w', encoding='utf-8') as out:
    for f, text in english_sentences:
        out.write(f"[{f}] {text}\n")

print(f"Found {len(english_sentences)} texts with potential English.")
