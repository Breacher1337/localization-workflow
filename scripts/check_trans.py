import sys
import os
import config
﻿import json
import csv
import os

plugin_dir = config.APPLICATION_CORE_DIR

print("Checking rules.csv translation...")
with open(os.path.join(plugin_dir, 'campaign', 'rules.csv'), 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    next(reader)
    row = next(reader)
    print(f"rules.csv sample: {row[4][:50]}")

print("\nChecking hull_plugins.csv translation...")
try:
    with open(os.path.join(plugin_dir, 'hullplugins', 'hull_plugins.csv'), 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)
        row = next(reader)
        print(f"hull_plugins.csv sample: {row[2][:50]}")
except Exception as e:
    print("hull_plugins.csv not found or error:", e)

print("\nChecking tips.json translation...")
try:
    with open(os.path.join(plugin_dir, 'strings', 'tips.json'), 'r', encoding='utf-8') as f:
        tips = json.load(f)
        print(f"tips.json sample: {tips['tips'][0]['tip'][:50]}")
except Exception as e:
    print("tips.json not found or error:", e)

