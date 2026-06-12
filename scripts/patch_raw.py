import os

rules_path = r".\plugins\JP_Lang_Pack\data\campaign\rules.csv"

with open(rules_path, 'r', encoding='utf-8') as f:
    content = f.read()

target_2 = '"We\'ve got plenty of supplies, so if we don\'t die of asphyxiation or freeze first... we\'ll get to slowly starve to death instead. It\'s just great."'
replace_2 = '"「物資はたくさんあるから、窒息死したり凍死したりしなければ…その代わり、ゆっくりと餓死することになるわね。最高だわ」"'

if target_2 in content:
    content = content.replace(target_2, replace_2)
    print("Replaced target 2 successfully!")
else:
    print("Target 2 not found in raw string.")
    # let's try a substring search
    idx = content.find("We've got plenty of supplies")
    if idx != -1:
        print("Found partial match at index", idx)
        print("Surrounding text:", repr(content[idx-20:idx+200]))

with open(rules_path, 'w', encoding='utf-8') as f:
    f.write(content)
