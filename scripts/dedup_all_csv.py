import csv
import sys
import os

plugin_dir = r".\plugins\JP_Lang_Pack\data"

files_to_dedup = [
    r"campaign\procgen\name_gen_data.csv",
    r"campaign\reports.csv"
]

for rel_path in files_to_dedup:
    path = os.path.join(plugin_dir, rel_path)
    if not os.path.exists(path):
        continue
        
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)

    seen = set()
    unique_rows = []
    duplicates_removed = 0

    for row in rows:
        row_tuple = tuple(row)
        if row_tuple in seen:
            duplicates_removed += 1
        else:
            seen.add(row_tuple)
            unique_rows.append(row)

    print(f"Removed {duplicates_removed} duplicate rows from {rel_path}.")

    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, lineterminator='\r\n')
        writer.writerow(header)
        writer.writerows(unique_rows)

print("Deduplication check complete.")
