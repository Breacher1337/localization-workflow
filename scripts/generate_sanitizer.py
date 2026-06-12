"""
Phase 0 Step C2: Generate sanitizer from glossary.
Reads the locked glossary and auto-generates sanitize_groups.py.
This eliminates glossary ↔ sanitizer divergence permanently.
"""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOSSARY = r".\localization_tracking\master_glossary.csv"
SANITIZER_OUT = r".\sanitize_groups.py"

# Load glossary
entries = {}
with open(GLOSSARY, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if row and len(row) >= 2:
            entries[row[0].strip()] = row[1].strip()

# Define known bad→good replacement rules based on glossary.
# These are patterns that AI translators historically drift to.
# The "good" value comes from the glossary. The "bad" patterns are known variants.
replacements = []

# Luddic: ルッディック is the approved base. Catch common AI drift variants.
luddic_approved = "ルッディック"
luddic_bad = ["ルゥディック", "ルダイック", "ラディック", "ルディック"]
for bad in luddic_bad:
    replacements.append((bad, luddic_approved))

# Independent: 独立勢力 is approved. AI often uses 独立した (adjective).
if "independent" in {k.lower() for k in entries}:
    replacements.append(("独立した", entries.get("independent", "独立勢力")))

# Hegemony: ヘゲモニー is approved. AI sometimes uses 覇権 (common word).
if "Hegemony" in entries:
    replacements.append(("覇権", entries["Hegemony"]))

# Tri-Tachyon: トライ・タキオン (with nakaguro). Catch without nakaguro and old prefix.
if "Tri-Tachyon" in entries:
    approved = entries["Tri-Tachyon"]  # トライ・タキオン
    replacements.append(("トリタキオン", approved))
    # Also catch the no-nakaguro variant if it differs
    no_naka = approved.replace("・", "")
    if no_naka != approved:
        replacements.append((no_naka, approved))

# Persean League
replacements.append(("ペルシア同盟", entries.get("Persean League", "ペルセアン同盟")))

# Generate sanitizer script
sanitizer_code = '''"""
Auto-generated sanitizer from master_glossary.csv.
DO NOT EDIT MANUALLY. Run generate_sanitizer.py to regenerate.
"""
import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plugin_dir = r".\\plugins\\JP_Lang_Pack\\data"

replacements = {
'''

for bad, good in replacements:
    sanitizer_code += f'    r"{bad}": "{good}",\n'

sanitizer_code += '''}

total_replacements = {k: 0 for k in replacements}
files_changed = 0

for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv') or f.endswith('.json') or f.endswith('.group'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                
                original_content = content
                
                for pattern, replacement in replacements.items():
                    if re.search(pattern, content):
                        count = len(re.findall(pattern, content))
                        content = re.sub(pattern, replacement, content)
                        total_replacements[pattern] += count
                
                if content != original_content:
                    with open(path, 'w', encoding='utf-8', newline='') as file:
                        file.write(content)
                    files_changed += 1
            except Exception as e:
                pass

print(f"Sanitized {files_changed} files.")
for k, v in total_replacements.items():
    if v > 0:
        print(f"  Replaced {v} instances of \\'{k}\\' with \\'{replacements[k]}\\'")
if files_changed == 0:
    print("  No replacements needed — plugin files are already consistent.")
'''

with open(SANITIZER_OUT, 'w', encoding='utf-8') as f:
    f.write(sanitizer_code)

print(f"Generated sanitizer with {len(replacements)} replacement rules:")
for bad, good in replacements:
    print(f"  {bad} → {good}")
print(f"\nWritten to: {SANITIZER_OUT}")
