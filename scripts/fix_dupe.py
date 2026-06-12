import csv

p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\procgen\name_gen_data.csv'

with open(p_plugin, 'r', encoding='utf-8') as f:
    plugin = list(csv.reader(f))

# Line 559 is index 559 (if we assume my script used enumerate with 0-index)
# Let's just search for it to be safe
for r in plugin:
    if len(r) >= 3 and r[0] == '????' and r[2] == 'planet':
        r[0] = '?????' # Change one of the dupes
        break # Only change the first one

with open(p_plugin, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator='\r\n')
    writer.writerows(plugin)

print('Fixed duplicate in name_gen_data.csv')
