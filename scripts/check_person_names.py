import csv

path = r".\plugins\JP_Lang_Pack\data\characters\person_names.csv"

with open(path, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    seen = {}
    duplicates = []
    for i, row in enumerate(reader):
        # The key usually consists of name, gender, category... Let's just create a key from all columns except id or something?
        # Application's log shows: [name | something | something | something | something]
        # Let's see the headers
        if i == 0:
            print("Headers:", reader.fieldnames)
            
        key = f"{row.get('name','')} | {row.get('gender','')} | {row.get('category','')}"
        # Let's just check the exact log format if we can, but we can just use the whole row except things that don't make it unique
        # Wait, the log key has 5 parts: name | unknown | unknown | unknown | unknown
        # Let's just find any rows that have the same values for the key columns
        # Let's look at the actual row
        row_tuple = tuple(row.values())
        if row_tuple in seen:
            duplicates.append((i+2, row_tuple, seen[row_tuple]))
        else:
            seen[row_tuple] = i+2
            
print(f"Found {len(duplicates)} exact duplicate rows.")

# Wait, the log shows `Duplicate key [????? |  | l | pluginern | ]`
# If we just look at the exact columns used to make the key
# Let's read the first 5 rows to see what columns there are.
with open(path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for _ in range(5):
        print(next(reader))
