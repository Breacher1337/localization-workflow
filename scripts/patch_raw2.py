import os

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"

with open(rules_path, 'r', encoding='utf-8') as f:
    content = f.read()

target_2 = '"""We\'ve got plenty of supplies, so if we don\'t die of boredom, we\'ll be waiting."" $HeOrShe sighs and closes the comm-link."'
replace_2 = '"「物資はたくさんあるから、退屈で死なない限り待たせてもらうよ」$HeOrShe はため息をつき、通信リンクを切った。"'

if target_2 in content:
    content = content.replace(target_2, replace_2)
    print("Replaced target 2 successfully!")
else:
    print("Target 2 not found in raw string.")

with open(rules_path, 'w', encoding='utf-8') as f:
    f.write(content)
