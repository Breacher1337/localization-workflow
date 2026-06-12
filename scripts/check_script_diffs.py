import sys
import os
import config
import csv
p_core = config.APPLICATION_CORE_DIR
p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

core = list(csv.reader(open(p_core, 'r', encoding='cp1252')))
plugin = list(csv.reader(open(p_plugin, 'r', encoding='utf-8')))

diffs = 0
for i in range(min(len(core), len(plugin))):
    c = core[i]
    m = plugin[i]
    if len(c) > 3 and len(m) > 3:
        # Ignore literal \n vs actual \n differences
        if c[3].replace('\n', '\\n') != m[3].replace('\n', '\\n'):
            diffs += 1
            if diffs == 1:
                print('Example diff:')
                print('Core:', repr(c[3]))
                print('Plugin:', repr(m[3]))

print('Total script column differences (ignoring newlines):', diffs)
