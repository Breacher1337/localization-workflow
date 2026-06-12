import json

with open('.\\translation_chunk_2.json', encoding='utf-8') as f:
    data = json.load(f)

with open('.\\texts.txt', 'w', encoding='utf-8') as f:
    for i, obj in enumerate(data):
        f.write(f"--- ITEM {i} ---\n{obj['text']}\n")
