import csv

plugin_path = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

with open(plugin_path, 'r', encoding='utf-8', newline='') as f:
    reader = csv.reader(f)
    headers = next(reader)
    script_idx = headers.index('script')
    
    for i, row in enumerate(reader):
        if len(row) > script_idx:
            script_val = row[script_idx]
            if '!' in script_val:
                print(f"Row {i+2}: {script_val}")
