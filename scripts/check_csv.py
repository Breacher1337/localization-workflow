import csv
import io
p = r'.\plugins\JP_Lang_Pack\data\weapons\weapon_data.csv'
with open(p, 'rb') as f:
    text = f.read().decode('utf-8')
try:
    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    for i, r in enumerate(rows):
        if len(r) == 0:
            print(f'Row {i} is empty!')
        elif r[0] == '':
            print(f'Row {i} name is empty!')
except Exception as e:
    print('Error:', e)
