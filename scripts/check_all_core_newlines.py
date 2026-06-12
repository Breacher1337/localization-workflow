import sys
import os
import config
import os
import csv

core_dir = config.APPLICATION_CORE_DIR
plugin_dir = r'.\plugins\JP_Lang_Pack\data'

for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv'):
            plugin_path = os.path.join(root, f)
            rel_path = os.path.relpath(plugin_path, plugin_dir)
            core_path = os.path.join(core_dir, rel_path)
            
            if os.path.exists(core_path):
                try:
                    with open(core_path, 'r', encoding='cp1252') as cf:
                        core_reader = list(csv.reader(cf))
                    core_literal_n = sum(c.count('\\n') for r in core_reader for c in r)
                    if core_literal_n > 0:
                        print(f'{rel_path} has {core_literal_n} legitimate literal \\n strings in the core application!')
                except Exception as e:
                    pass
