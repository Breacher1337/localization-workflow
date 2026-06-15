import json
import ast
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

chunks_path = r"e:\lamesa\2026\application-jp\data\chunks\phase4_approved.json"

with open(chunks_path, "r", encoding="utf-8") as f:
    data = json.load(f)

def get_translation_from_dict(parsed_dict):
    preferred_keys = ["translated_text", "translation", "translated"]
    for k in preferred_keys:
        if k in parsed_dict and isinstance(parsed_dict[k], str):
            return parsed_dict[k]
            
    # Check for any string containing non-ASCII
    for k, v in parsed_dict.items():
        if isinstance(v, str) and any(ord(c) > 127 for c in v):
            return v
            
    # Check for any string that isn't metadata keys
    for k, v in parsed_dict.items():
        if k not in ["context_tag", "chunk_type"] and isinstance(v, str):
            return v
    return None

count = 0
for idx, item in enumerate(data):
    transl = item.get("translation", "")
    if not isinstance(transl, str):
        continue
    
    t_clean = transl.strip()
    if t_clean.startswith("{") and ("translated_text" in t_clean or "translation" in t_clean or "source_text" in t_clean):
        # Strip trailing text after the closing brace if present
        last_brace = t_clean.rfind("}")
        if last_brace != -1:
            t_clean = t_clean[:last_brace+1]
        try:
            parsed = ast.literal_eval(t_clean)
            if isinstance(parsed, dict):
                val = get_translation_from_dict(parsed)
                if val:
                    item["translation"] = val
                    print(f"Healed index {idx} ({item.get('row_key')}): done")
                    count += 1
        except Exception as e:
            print(f"Error parsing index {idx}: {e}")

if count > 0:
    with open(chunks_path, "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Successfully healed and saved {count} translations in phase4_approved.json")
else:
    print("No translations needed healing or healing failed.")
