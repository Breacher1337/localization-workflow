import csv
import json
import os

def inject():
    # Load all translations
    tr = {}
    for i in range(1, 7):
        fname = f'desc_chunk_{i}_ja.json'
        alt_fname = f'chunk_{i}_ja.json'
        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                chunk_tr = json.load(f)
                tr.update(chunk_tr)
        elif os.path.exists(alt_fname):
            with open(alt_fname, 'r', encoding='utf-8') as f:
                chunk_tr = json.load(f)
                tr.update(chunk_tr)
        else:
            print(f"Warning: {fname} not found. Proceeding with missing translations.")

    out_rows = []
    with open('descriptions.csv', 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            for key in ['text1', 'text2', 'text3']:
                if key in row and row[key].strip() != '':
                    orig = row[key]
                    if orig in tr:
                        row[key] = tr[orig]
            out_rows.append(row)

    with open('descriptions_translated.csv', 'w', encoding='utf-8', newline='') as out:
        writer = csv.DictWriter(out, fieldnames=fieldnames, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        writer.writerows(out_rows)
        
    print("Wrote translated descriptions to descriptions_translated.csv")

if __name__ == "__main__":
    inject()
