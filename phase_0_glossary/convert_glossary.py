# phase_0_glossary/convert_glossary.py
import json
import csv
import os
from datetime import datetime, timezone

def main():
    csv_path = r".\localization_tracking\master_glossary.csv"
    json_path = r".\phase_0_glossary\locked_glossary_v1.json"
    
    entries = []
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            term_en = row["English Source"].strip()
            ja = row["Japanese Translation"].strip()
            type_val = row["Type"].strip()
            nuance = row["Context & Localization Nuance"].strip()
            status = row["Status"].strip()
            
            if not term_en or not ja:
                continue
                
            translation_obj = {
                "ja": ja,
                "context": type_val,
                "pos": "noun",
                "nuance": nuance,
                "status": status
            }
            
            # Prevent duplicates by merging matching term_en entries
            existing = next((e for e in entries if e["term_en"] == term_en), None)
            if existing:
                existing["translations"].append(translation_obj)
            else:
                entries.append({
                    "term_en": term_en,
                    "translations": [translation_obj]
                })
                
    glossary_data = {
        "_meta": {
            "version": "1.0",
            "locked_by": "human_arbiter",
            "locked_at": datetime.now(timezone.utc).isoformat(),
            "source": "localization_tracking/master_glossary.csv",
            "entry_count": len(entries)
        },
        "entries": entries
    }
    
    os.makedirs(os.path.dirname(json_path), exist_ok=True)
    with open(json_path, "w", encoding="utf-8", newline="") as f:
        json.dump(glossary_data, f, ensure_ascii=False, indent=2)
    print(f"Glossary successfully locked with {len(entries)} entries.")

if __name__ == "__main__":
    main()
