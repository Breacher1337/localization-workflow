import sys
import os
import config
import csv
p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\procgen\name_gen_data.csv'
p_core = config.APPLICATION_CORE_DIR

plugin = list(csv.reader(open(p_plugin, 'r', encoding='utf-8')))
core = list(csv.reader(open(p_core, 'r', encoding='cp1252')))

keys = {}
for i, r in enumerate(plugin):
    if len(r) < 3: continue
    key = (r[0], r[1], r[2])
    if key in keys:
        print('Dupe found at lines:', keys[key], i)
        print('Core 1:', core[keys[key]][:3])
        print('Core 2:', core[i][:3])
    else:
        keys[key] = i
