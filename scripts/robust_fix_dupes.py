import sys
import os
import config
import csv
p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\procgen\name_gen_data.csv'
p_core = config.APPLICATION_CORE_DIR

plugin = list(csv.reader(open(p_plugin, 'r', encoding='utf-8')))
core = list(csv.reader(open(p_core, 'r', encoding='cp1252')))

seen = set()
dupes_fixed = 0

for i, r in enumerate(plugin):
    if len(r) < 3: continue
    # The key is name + category + tags.
    # Actually, Application's error says: [name | category | tags]
    # Wait, the tags column can be empty.
    key = (r[0], r[1], r[2])
    
    if key in seen:
        # Revert to core name
        if i < len(core):
            r[0] = core[i][0]
        else:
            r[0] = r[0] + str(dupes_fixed)
            
        new_key = (r[0], r[1], r[2])
        if new_key in seen:
            r[0] = r[0] + "_" + str(dupes_fixed)
            
        seen.add((r[0], r[1], r[2]))
        dupes_fixed += 1
    else:
        seen.add(key)

with open(p_plugin, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator='\r\n')
    writer.writerows(plugin)

print('Fixed', dupes_fixed, 'duplicate keys')
