import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

chunks_path = r"e:\lamesa\2026\application-jp\data\chunks\phase4_approved.json"

with open(chunks_path, "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:
    if "ome_askHire" in item.get("source_text", "") or "ome_askHire" in item.get("translation", ""):
        print(item)
