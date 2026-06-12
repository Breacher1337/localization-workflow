import sys
import os
import config
import os
import csv
import json
import re

core_dir = config.APPLICATION_CORE_DIR
plugin_dir = r".\plugins\JP_Lang_Pack\data"
output_csv = r".\localization_masterlist.csv"

# Potential translatable column names in CSVs
translatable_cols = {'name', 'desc', 'text', 'options', 'displayName', 'designation', 'primaryRoleStr', 'personNamePrefix', 'shipNamePrefix', 'hisOrHer', 'heOrShe', 'himOrHer', 'text1', 'text2', 'text3', 'text4', 'text5', 'subject', 'summary', 'assessment'}


def contains_japanese(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if re.search(r'[あ-んア-ン一-龥]', content):
                return True
    except:
        pass
    return False

def is_translatable_csv(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = next(reader)
            if any(col in translatable_cols for col in header):
                return True
    except:
        pass
    return False

def is_translatable_json(file_path):
    # strings.json, ship_names.json, etc. 
    # For now, if it's in strings/ or contains strings with english text
    if "strings" in file_path.lower() or "names" in file_path.lower() or "rules" in file_path.lower():
        return True
    return False

core_files = set()
for root, _, files in os.walk(core_dir):
    for f in files:
        if f.endswith('.csv') or f.endswith('.json') or f.endswith('.group'):
            rel_path = os.path.relpath(os.path.join(root, f), core_dir)
            core_files.add(rel_path)

plugin_files = set()
for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv') or f.endswith('.json') or f.endswith('.group'):
            rel_path = os.path.relpath(os.path.join(root, f), plugin_dir)
            plugin_files.add(rel_path)

all_files = core_files.union(plugin_files)
results = []

for rel_path in sorted(all_files):
    core_path = os.path.join(core_dir, rel_path)
    plugin_path = os.path.join(plugin_dir, rel_path)
    
    in_core = os.path.exists(core_path)
    in_plugin = os.path.exists(plugin_path)
    
    is_translatable = False
    status = "Untranslated"
    
    check_path = plugin_path if in_plugin else core_path
    
    if rel_path.endswith('.csv'):
        is_translatable = is_translatable_csv(check_path)
    elif rel_path.endswith('.json') or rel_path.endswith('.group'):
        # Just consider all .group and specific .jsons as translatable
        if rel_path.endswith('.group'):
            is_translatable = True
        else:
            is_translatable = is_translatable_json(check_path)
        
    if is_translatable:
        if in_plugin and contains_japanese(plugin_path):
            status = "Translated (Contains Japanese)"
        elif not in_plugin:
            status = "Not in Plugin Folder"
        else:
            status = "In Plugin Folder (English)"
            
        results.append({
            'File Path': rel_path,
            'Type': 'CSV' if rel_path.endswith('.csv') else 'JSON',
            'In Core Application': 'Yes' if in_core else 'No',
            'In Plugin Folder': 'Yes' if in_plugin else 'No',
            'Status': status
        })

with open(output_csv, 'w', encoding='utf-8', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=['File Path', 'Type', 'In Core Application', 'In Plugin Folder', 'Status'])
    writer.writeheader()
    writer.writerows(results)

print(f"Generated masterlist with {len(results)} translatable files out of {len(all_files)} total data files.")
