import csv

with open('descriptions_translated.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    empty_ids = 0
    for i, row in enumerate(reader):
        if len(row) < 2 or not row[0]:
            print(f"Row {i+2}: {row}")
            empty_ids += 1
            if empty_ids > 10:
                break
