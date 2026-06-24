import os
import re
import csv
import json
import shutil

# Target Paths
strings_jp = r"E:\lamesa\2026\application-jp\plugins\JP_Lang_Pack\data\strings\strings.json"
strings_en = r"E:\lamesa\2026\application-jp\data\json_chunks\strings.json"

rules_jp = r"E:\lamesa\2026\application-jp\plugins\JP_Lang_Pack\data\campaign\rules.csv"
rules_en = r"C:\Program Files (x86)\Acme Corp\Application\application-core\data\campaign\rules.csv"

# Backup Paths
backup_dir = r"E:\lamesa\2026\application-jp\localization_tracking\backup"
os.makedirs(backup_dir, exist_ok=True)

shutil.copy(strings_jp, os.path.join(backup_dir, "strings.json.bak"))
shutil.copy(rules_jp, os.path.join(backup_dir, "rules.csv.bak"))
print("[INFO] Backups created in localization_tracking/backup/")

# Tolerant JSON parser
def parse_json_tolerant(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("\ufeff"):
        content = content[1:]
    lines = content.split("\n")
    cleaned = []
    for line in lines:
        in_string = False
        escape = False
        result = []
        for ch in line:
            if escape:
                result.append(ch)
                escape = False
                continue
            if ch == "\\":
                escape = True
                result.append(ch)
                continue
            if ch == '"':
                in_string = not in_string
                result.append(ch)
                continue
            if ch == "#" and not in_string:
                break
            result.append(ch)
        cleaned.append("".join(result))
    text = "\n".join(cleaned)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    text = text.strip()
    if text.endswith(','):
        text = text[:-1].strip()
    text = re.sub(r'\b(\d+\.?\d*)f\b', r'\1', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    bare_key_re = re.compile(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:\s*)')
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or stripped.startswith('"') or stripped[0] in "]}),":
            result.append(line)
            continue
        m = bare_key_re.match(line)
        if m:
            leading = m.group(1)
            key = m.group(2)
            colon = m.group(3)
            rest = line[m.end():]
            line = f'{leading}"{key}"{colon}{rest}'
        result.append(line)
    return json.loads("\n".join(result))

# Regex for matching trailing placeholders
trailing_vars_re = re.compile(r"(\s+(?:\$[a-zA-Z0-9_\.]+|%[0-9]*\.?[0-9]*[sdfiexXo]|\{[a-zA-Z0-9_\.]+\}))+$")

# 1. Clean strings.json
print("[INFO] Cleaning strings.json...")
en_data = parse_json_tolerant(strings_en)
jp_data = parse_json_tolerant(strings_jp)

clean_strings_count = 0

for section_name, section in jp_data.items():
    if isinstance(section, dict):
        en_section = en_data.get(section_name, {})
        for key, jp_val in section.items():
            if isinstance(jp_val, str) and isinstance(en_section, dict):
                en_val = en_section.get(key)
                if isinstance(en_val, str):
                    jp_match = trailing_vars_re.search(jp_val)
                    en_match = trailing_vars_re.search(en_val)
                    
                    jp_trailing = jp_match.group(0) if jp_match else None
                    en_trailing = en_match.group(0) if en_match else None
                    
                    if jp_trailing:
                        if not en_trailing:
                            # Strip all trailing placeholders
                            section[key] = jp_val[:jp_match.start()]
                            clean_strings_count += 1
                        elif jp_trailing.strip() != en_trailing.strip():
                            # Mismatch: strip trailing from jp and restore what en originally had
                            base_jp = jp_val[:jp_match.start()]
                            section[key] = base_jp + en_trailing
                            clean_strings_count += 1

with open(strings_jp, "w", encoding="utf-8") as f:
    json.dump(jp_data, f, ensure_ascii=False, indent=2)

print(f"[INFO] strings.json cleaned: {clean_strings_count} entries fixed.")

# 2. Clean rules.csv
print("[INFO] Cleaning rules.csv...")
en_rows = []
with open(rules_en, "r", encoding="cp1252", errors="ignore") as f:
    reader = csv.reader(f)
    en_header = next(reader)
    en_rows = list(reader)

with open(rules_jp, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    jp_header = next(reader)
    jp_rows = list(reader)

text_cols = [i for i, h in enumerate(en_header) if h.lower() in ('text', 'options')]
clean_rules_count = 0

for idx, jp_row in enumerate(jp_rows):
    if idx < len(en_rows):
        en_row = en_rows[idx]
        # Verify alignment using the 'id' column
        jp_id = jp_row[0] if len(jp_row) > 0 else ""
        en_id = en_row[0] if len(en_row) > 0 else ""
        
        if jp_id == en_id:
            for col_idx in text_cols:
                if col_idx < len(jp_row) and col_idx < len(en_row):
                    jp_val = jp_row[col_idx]
                    en_val = en_row[col_idx]
                    
                    if jp_val and en_val:
                        jp_match = trailing_vars_re.search(jp_val)
                        en_match = trailing_vars_re.search(en_val)
                        
                        jp_trailing = jp_match.group(0) if jp_match else None
                        en_trailing = en_match.group(0) if en_match else None
                        
                        if jp_trailing:
                            if not en_trailing:
                                jp_row[col_idx] = jp_val[:jp_match.start()]
                                clean_rules_count += 1
                            elif jp_trailing.strip() != en_trailing.strip():
                                base_jp = jp_val[:jp_match.start()]
                                jp_row[col_idx] = base_jp + en_trailing
                                clean_rules_count += 1
        else:
            print(f"[WARN] Alignment mismatch at row {idx}: JP id='{jp_id}', EN id='{en_id}'")

with open(rules_jp, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(jp_header)
    writer.writerows(jp_rows)

print(f"[INFO] rules.csv cleaned: {clean_rules_count} cells fixed.")
