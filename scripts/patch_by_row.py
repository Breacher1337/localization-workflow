import csv

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"
csv.field_size_limit(10000000)

rows = []
with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append(row)

replace_1 = "「それで、若き見習い騎士――いや、元見習いと言うべきかしら――が、宇宙船乗りにそんな口を利くなんて、ずいぶん勇敢だと思ったわ。あなたが彼女をそそのかしたの？」"
replace_2 = "「物資はたくさんあるから、窒息死したり凍死したりしなければ…その代わり、ゆっくりと餓死することになるわね。最高だわ」"

text_idx = rows[0].index('text')
replaced = 0

# The indices are 1778 and 7122 (0-indexed or 1-indexed? check_untranslated used enumerate which is 0-indexed)
idx_1 = 1778
idx_2 = 7122

if "plenty of supplies" in rows[idx_2][text_idx]:
    rows[idx_2][text_idx] = replace_2
    replaced += 1
    
if "Knight Initiate" in rows[idx_1][text_idx]:
    rows[idx_1][text_idx] = replace_1
    replaced += 1

if replaced > 0:
    with open(rules_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"Successfully patched {replaced} remaining english lines.")
else:
    print("Could not find the target lines by row index. Here is what is there:")
    print("Row 1778:", rows[idx_1][text_idx])
    print("Row 7122:", rows[idx_2][text_idx])
