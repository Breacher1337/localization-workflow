import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

chunks_path = r"e:\lamesa\2026\application-jp\data\chunks\phase4_approved.json"

with open(chunks_path, "r", encoding="utf-8") as f:
    data = json.load(f)

print("Sample options translations in phase4_approved.json:")
count = 0
for item in data:
    if "rules.csv" in item.get("source_file", "") and item.get("column") == "options":
        # Print source and translation safely
        src = item.get('source_text')
        transl = item.get('translation')
        print(f"Source: {src}")
        print(f"Transl: {transl}")
        print("-" * 50)
        count += 1
        if count >= 20:
            break
