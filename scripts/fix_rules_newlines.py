import csv
import io

p2 = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

# Read original
with open(p2, 'r', encoding='utf-8') as f:
    reader = list(csv.reader(f))

# Fix literal \n in columns 4 (text), 5 (options) and 6 (notes)
fixed = 0
for r in reader:
    for i in [4, 5, 6]:
        if i < len(r) and '\\n' in r[i]:
            r[i] = r[i].replace('\\n', '\n')
            fixed += 1

# Write back
with open(p2, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator='\r\n')
    writer.writerows(reader)

print('Fixed', fixed, 'cells in rules.csv')
