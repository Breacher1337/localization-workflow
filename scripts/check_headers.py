import sys
import os
import config
import os
import csv

core_dir = config.APPLICATION_CORE_DIR

for root, _, files in os.walk(core_dir):
    for f in files:
        if f.endswith('.csv'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as csvfile:
                    reader = csv.reader(csvfile)
                    header = next(reader)
                    rel_path = os.path.relpath(path, core_dir)
                    print(f"{rel_path}: {header[:10]}...")
            except Exception as e:
                print(f"Error reading {f}: {e}")
