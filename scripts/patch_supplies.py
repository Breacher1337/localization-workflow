import csv

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"
csv.field_size_limit(10000000)

rows = []
with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append(row)

replace_2 = "「物資はたくさんあるから、窒息死したり凍死したりしなければ…その代わり、ゆっくりと餓死することになるわね。最高だわ」"

text_idx = rows[0].index('text')
replaced = 0

for row in rows:
    if len(row) > text_idx:
        text = row[text_idx]
        if "plenty of supplies" in text and "asphyxiation" in text:
            row[text_idx] = replace_2
            replaced += 1

if replaced > 0:
    with open(rules_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"Successfully patched {replaced} remaining english lines.")
else:
    print("Could not find the 'plenty of supplies' string.")
