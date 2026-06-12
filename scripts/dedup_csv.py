import csv
import sys

path = r".\plugins\JP_Lang_Pack\data\characters\person_names.csv"

with open(path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

seen = set()
unique_rows = []
duplicates_removed = 0

for row in rows:
    # Key is everything except maybe some empty tail columns? 
    # Actually, the entire row can be the key. If it's an exact duplicate row, we drop it.
    # Application's key: name | gender | usage | category | tags
    # Let's just use the whole row as a tuple
    row_tuple = tuple(row)
    if row_tuple in seen:
        duplicates_removed += 1
    else:
        seen.add(row_tuple)
        unique_rows.append(row)

print(f"Removed {duplicates_removed} duplicate rows.")

with open(path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator='\r\n')
    writer.writerow(header)
    writer.writerows(unique_rows)

print("Deduplication complete.")
