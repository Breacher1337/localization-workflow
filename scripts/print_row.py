import csv
import sys

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"
csv.field_size_limit(10000000)

with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i == 7122:
            print("Row 7122 text column:", row[row.index('We\'ve got plenty of supplies, so if we don\'t die of asphyxiation or freeze first... we\'ll get to slowly starve to death instead. It\'s just great.') if 'We\'ve got plenty of supplies, so if we don\'t die of asphyxiation or freeze first... we\'ll get to slowly starve to death instead. It\'s just great.' in row else row[0]])
            for j, c in enumerate(row):
                if "supplies" in c:
                    print(f"Col {j}: {c}")
            break
