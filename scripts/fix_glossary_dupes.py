"""Fix duplicate keys in glossary: remove duplicate Hegemony, disambiguate corporation."""
import csv
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOSSARY = r".\localization_tracking\master_glossary.csv"

with open(GLOSSARY, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

print(f"Before: {len(rows)} rows")

# Remove duplicate Hegemony (keep the one with more context)
seen_keys = {}
deduped = []
removed = []
for row in rows:
    if not row:
        continue
    key = row[0].strip().lower()
    if key in seen_keys:
        # Keep the one with more context (longer row)
        existing = deduped[seen_keys[key]]
        existing_context = existing[3] if len(existing) > 3 else ""
        new_context = row[3] if len(row) > 3 else ""
        if len(new_context) > len(existing_context):
            removed.append(existing[0])
            deduped[seen_keys[key]] = row
        else:
            removed.append(row[0])
        continue
    seen_keys[key] = len(deduped)
    deduped.append(row)

# Disambiguate corporation vs Corporation by making keys unique
for i, row in enumerate(deduped):
    if row[0] == "corporation":
        row[0] = "corporation (noun)"
    elif row[0] == "Corporation":
        row[0] = "Corporation (suffix)"

with open(GLOSSARY, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for row in deduped:
        writer.writerow(row)

print(f"After: {len(deduped)} rows")
print(f"Removed duplicates: {removed}")
