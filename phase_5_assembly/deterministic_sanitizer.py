import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config
# phase_5_assembly/deterministic_sanitizer.py
import os
import csv
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

PROJECT_ROOT = r"."
VANILLA_DATA = config.APPLICATION_CORE_DIR
PLUGIN_DATA = os.path.join(PROJECT_ROOT, r"plugins\JP_Lang_Pack\data")

def sanitize_csv_file(filepath):
    # Enforce NO BOM
    with open(filepath, "rb") as f:
        content_bytes = f.read()
    
    # Strip UTF-8 BOM if present
    if content_bytes.startswith(b"\xef\xbb\xbf"):
        content_bytes = content_bytes[3:]
        
        # Write back without BOM only if BOM was found
        with open(filepath, "wb") as f:
            f.write(content_bytes)

def handle_duplicate_composite_keys():
    # 1. name_gen_data.csv
    name_gen_path = os.path.join(PLUGIN_DATA, r"campaign\procgen\name_gen_data.csv")
    vanilla_name_gen_path = os.path.join(VANILLA_DATA, r"campaign\procgen\name_gen_data.csv")
    
    if os.path.exists(name_gen_path) and os.path.exists(vanilla_name_gen_path):
        with open(name_gen_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            
        with open(vanilla_name_gen_path, "r", encoding="cp1252") as f:
            v_reader = csv.reader(f)
            v_header = next(v_reader)
            v_rows = list(v_reader)
            
        name_idx = header.index("name")
        tags_idx = header.index("tags")
        
        seen = {} # composite key -> line number
        reverted_count = 0
        
        for idx, row in enumerate(rows):
            if not row:
                continue
            name_val = row[name_idx].strip()
            if not name_val:
                continue
            tags_val = row[tags_idx].strip()
            composite = (name_val, tags_val)
            
            if composite in seen:
                # Collision! Revert to vanilla English
                if idx < len(v_rows):
                    row[name_idx] = v_rows[idx][name_idx]
                    reverted_count += 1
            else:
                seen[composite] = idx
                
        if reverted_count > 0:
            print(f"Reverted {reverted_count} duplicate composite keys in name_gen_data.csv")
            with open(name_gen_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)
                
    # 2. person_names.csv
    person_names_path = os.path.join(PLUGIN_DATA, r"characters\person_names.csv")
    vanilla_person_names_path = os.path.join(VANILLA_DATA, r"characters\person_names.csv")
    
    if os.path.exists(person_names_path) and os.path.exists(vanilla_person_names_path):
        with open(person_names_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            rows = list(reader)
            
        with open(vanilla_person_names_path, "r", encoding="utf-8") as f:
            v_reader = csv.reader(f)
            v_header = next(v_reader)
            v_rows = list(v_reader)
            
        name_idx = header.index("name")
        gender_idx = header.index("gender")
        usage_idx = header.index("usage")
        category_idx = header.index("category")
        
        seen = {}
        reverted_count = 0
        for idx, row in enumerate(rows):
            if not row:
                continue
            name_val = row[name_idx].strip()
            if not name_val:
                continue
            gender_val = row[gender_idx].strip()
            usage_val = row[usage_idx].strip()
            category_val = row[category_idx].strip()
            composite = (name_val, gender_val, usage_val, category_val)
            
            if composite in seen:
                # Collision! Revert to vanilla English
                if idx < len(v_rows):
                    row[name_idx] = v_rows[idx][name_idx]
                    reverted_count += 1
            else:
                seen[composite] = idx
                
        if reverted_count > 0:
            print(f"Reverted {reverted_count} duplicate composite keys in person_names.csv")
            with open(person_names_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(header)
                writer.writerows(rows)

def main():
    print("Phase 5 Assembly - Deterministic Sanitizer")
    
    # Walk all files in the output directory
    for root, dirs, files in os.walk(PLUGIN_DATA):
        for f in files:
            path = os.path.join(root, f)
            if f.endswith(".csv"):
                sanitize_csv_file(path)
                
    # Handle duplicate key collisions to prevent application crash
    handle_duplicate_composite_keys()
    print("Sanitization completed successfully.")

if __name__ == "__main__":
    main()
