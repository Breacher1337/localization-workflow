import sys
import os
import config
import csv
p_core = config.APPLICATION_CORE_DIR
p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

core = list(csv.reader(open(p_core, 'r', encoding='cp1252')))
plugin = list(csv.reader(open(p_plugin, 'r', encoding='utf-8')))

for i in range(len(plugin)):
    if len(plugin[i]) >= 4 and len(core[i]) >= 4:
        plugin[i][0] = core[i][0]
        plugin[i][1] = core[i][1]
        plugin[i][2] = core[i][2]
        plugin[i][3] = core[i][3]

with open(p_plugin, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator='\r\n')
    writer.writerows(plugin)

print('Restored rules.csv internal logic columns again!')
