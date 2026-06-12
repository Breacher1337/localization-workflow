import os
import csv
import json

plugin_dir = r".\plugins\JP_Lang_Pack\data"

files_to_update = [
    r"characters\skills\aptitude_data.csv",
    r"characters\skills\skill_data.csv",
    r"shipsystems\ship_systems.csv",
    r"weapons\weapon_data.csv",
    r"world\groups\groups.csv"
]

# Load translations
translations = {}
for i in [1, 2]:
    path = fr".\phase3_chunk_{i}_ja.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            translations.update(data)
            print(f"Loaded chunk {i} ({len(data)} items)")

print(f"Total loaded translations: {len(translations)}")

# Group translations by file
file_translations = {}
for key, text in translations.items():
    file_path, row_id, col = key.split('|')
    if file_path not in file_translations:
        file_translations[file_path] = {}
    if row_id not in file_translations[file_path]:
        file_translations[file_path][row_id] = {}
    file_translations[file_path][row_id][col] = text

# Update files
for f in files_to_update:
    if f not in file_translations:
        continue
    
    dst = os.path.join(plugin_dir, f)
    
    rows = []
    header = []
    updated_count = 0
    # Base application CSVs might be cp1252
    with open(dst, 'r', encoding='cp1252', errors='replace') as file:
        reader = csv.reader(file)
        header = next(reader)
        # find ID column
        id_col_idx = 0
        if 'id' in header:
            id_col_idx = header.index('id')
            
        for row in reader:
            if not row:
                rows.append(row)
                continue
            row_id = row[id_col_idx]
            if row_id in file_translations[f]:
                for col_name, text in file_translations[f][row_id].items():
                    if col_name in header:
                        col_idx = header.index(col_name)
                        if col_idx < len(row):
                            row[col_idx] = text
                        else:
                            # pad row
                            row.extend([''] * (col_idx - len(row) + 1))
                            row[col_idx] = text
                        updated_count += 1
            rows.append(row)

    # Write back in UTF-8
    with open(dst, 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        for row in rows:
            writer.writerow(row)
            
    print(f"Updated {f}: {updated_count} cells translated.")
