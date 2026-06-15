import json
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

chunks_path = r"e:\lamesa\2026\application-jp\data\chunks\phase4_approved.json"

with open(chunks_path, "r", encoding="utf-8") as f:
    data = json.load(f)

count = 0
for idx, item in enumerate(data):
    transl = item.get("translation", "")
    if not isinstance(transl, str):
        continue
    # Check if translation looks like a dict string
    if (transl.strip().startswith("{") and "translated_text" in transl) or (transl.strip().startswith("{") and "translation" in transl):
        print(f"Index: {idx}, Row: {item.get('row_key')}, Col: {item.get('column')}")
        print(f"Transl: {transl}")
        print("-" * 80)
        count += 1

print(f"Found {count} dict-like translations.")
