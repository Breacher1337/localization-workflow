import os
import csv

plugin_dir = r".\plugins\JP_Lang_Pack\data"

replace_candidates = []
for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as f_obj:
                    reader = csv.reader(f_obj)
                    headers = next(reader)
                    # Often 'id' or 'ID'
                    has_id = any(h.lower() == 'id' for h in headers)
                    if not has_id:
                        rel_path = os.path.relpath(path, plugin_dir)
                        replace_candidates.append(rel_path.replace('\\', '/'))
                        print(f"{rel_path}: {headers}")
            except Exception as e:
                pass

print("\nFiles without 'id':")
for p in replace_candidates:
    print(f'"data/{p}",')
