import csv
import os

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"
csv.field_size_limit(10000000)

rows = []
with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append(row)

target_2 = "We've got plenty of supplies, so if we don't die of asphyxiation"
replace_2 = "「物資はたくさんあるから、窒息死したり凍死したりしなければ…その代わり、ゆっくりと餓死することになるわね。最高だわ」"

text_idx = rows[0].index('text')
replaced = 0

for row in rows:
    if len(row) > text_idx:
        # Just check if 'plenty of supplies' is in the text
        if "plenty of supplies" in row[text_idx] and "asphyxiation" in row[text_idx]:
            row[text_idx] = replace_2
            replaced += 1

if replaced > 0:
    with open(rules_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"Successfully patched {replaced} remaining english lines.")
else:
    print("Could not find the target lines to patch.")
