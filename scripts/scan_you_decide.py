import os
import json
import csv

plugin_dir = r".\plugins\JP_Lang_Pack\data"
rules_path = os.path.join(plugin_dir, r"campaign\rules.csv")
strings_path = os.path.join(plugin_dir, r"strings\strings.json")

print("--- Scanning strings.json ---")
with open(strings_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "You decide to" in line:
        print(f"strings.json:{i+1}: {line.strip()}")

print("\n--- Scanning rules.csv ---")
with open(rules_path, 'r', encoding='utf-8', errors='ignore') as f:
    reader = csv.reader(f)
    try:
        header = next(reader)
        for i, row in enumerate(reader):
            for j, cell in enumerate(row):
                if "You decide to" in cell:
                    print(f"rules.csv row {i+2} col {header[j] if j < len(header) else j}: {cell}")
    except Exception as e:
        print(f"Error reading rules.csv: {e}")
