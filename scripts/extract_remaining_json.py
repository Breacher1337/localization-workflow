import sys
import os
import config
import os
import json
import csv

plugin_dir = r".\plugins\JP_Lang_Pack\data"
core_dir = config.APPLICATION_CORE_DIR
masterlist_csv = r".\localization_masterlist.csv"

files_to_translate = []
with open(masterlist_csv, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Type'] == 'JSON' and row['Status'] != 'Translated (Contains Japanese)':
            files_to_translate.append(row['File Path'])

print(f"Found {len(files_to_translate)} JSON/group files to process.")

def extract_strings_from_json(data, path_prefix, extracted):
    if isinstance(data, dict):
        for k, v in data.items():
            if k in ['name', 'displayName', 'description', 'desc', 'text', 'music', 'sound', 'graphics', 'color', 'icon']: # exclude non-text
                if isinstance(v, str) and len(v) > 0 and k in ['name', 'displayName', 'description', 'desc', 'text']:
                    extracted[f"{path_prefix}|{k}"] = v
            else:
                extract_strings_from_json(v, f"{path_prefix}|{k}", extracted)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            extract_strings_from_json(item, f"{path_prefix}|{i}", extracted)

# Because group files are not always strict JSON (they use HJSON-like syntax in Application, with unquoted keys and trailing commas)
# Let's just pass the raw file to the subagent instead of parsing it to JSON!
# The subagent can read the .group file and pluginify it using sed or replace_file_content!
# Wait, replacing content in a 1000-line .group file via subagent could be messy.
# Since we are automating, let's just make a script that copies the group files over. The subagent will translate them in place.

import shutil
for rel_path in files_to_translate:
    core_path = os.path.join(core_dir, rel_path)
    plugin_path = os.path.join(plugin_dir, rel_path)
    if os.path.exists(core_path) and not os.path.exists(plugin_path):
        os.makedirs(os.path.dirname(plugin_path), exist_ok=True)
        shutil.copy2(core_path, plugin_path)

print("Copied all missing JSON/group files to plugin folder for direct translation.")
