import csv
import os

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"
csv.field_size_limit(10000000)

rows = []
with open(rules_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        rows.append(row)

target_1 = "And a young Knight Initiate - former Initiate, I should say - spoke well of your simple words on Hesperus which set him on a new Path."
replace_1 = "「それで、若き見習い騎士――いや、元見習いと言うべきかしら――が、ヘスペルスでのあなたのシンプルな言葉が、彼を新しい道へと導いたと高く評価していたわ」"

target_2 = "We've got plenty of supplies, so if we don't die of asphyxiation or freeze first... we'll get to slowly starve to death instead. It's just great."
replace_2 = "「物資はたくさんあるから、窒息死したり凍死したりしなければ…その代わり、ゆっくりと餓死することになるわね。最高だわ」"

text_idx = rows[0].index('text')
replaced = 0

for row in rows:
    if len(row) > text_idx:
        if target_1 in row[text_idx]:
            row[text_idx] = row[text_idx].replace(target_1, replace_1)
            replaced += 1
        if target_2 in row[text_idx]:
            row[text_idx] = row[text_idx].replace(target_2, replace_2)
            replaced += 1

if replaced > 0:
    with open(rules_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)
    print(f"Successfully patched {replaced} remaining english lines.")
else:
    print("Could not find the target lines to patch.")
