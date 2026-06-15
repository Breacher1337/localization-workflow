import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

chunks_path = r"e:\lamesa\2026\application-jp\data\chunks\phase4_approved.json"

with open(chunks_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for idx in [9560, 9562, 9564, 10027]:
    if idx < len(data):
        print(f"Index: {idx}, Row: {data[idx].get('row_key')}, Col: {data[idx].get('column')}")
        print(f"Source: {data[idx].get('source_text')}")
        print(f"Transl: {data[idx].get('translation')}")
        print("-" * 80)
