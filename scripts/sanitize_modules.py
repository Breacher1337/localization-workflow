"""
Auto-generated sanitizer from master_glossary.csv.
DO NOT EDIT MANUALLY. Run generate_sanitizer.py to regenerate.
"""
import os
import re
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

plugin_dir = r".\plugins\JP_Lang_Pack\data"

replacements = {
    r"ルゥディック": "ルッディック",
    r"ルダイック": "ルッディック",
    r"ラディック": "ルッディック",
    r"ルディック": "ルッディック",
    r"独立した": "独立勢力",
    r"覇権": "ヘゲモニー",
    r"トリタキオン": "トライ・タキオン",
    r"トライタキオン": "トライ・タキオン",
    r"ペルシア同盟": "ペルセアン同盟",
}

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
        print(f"  Replaced {v} instances of \'{k}\' with \'{replacements[k]}\'")
if files_changed == 0:
    print("  No replacements needed — plugin files are already consistent.")
