import sys
import os
import config
import os
import csv
import json

core_dir = config.APPLICATION_CORE_DIR
plugin_dir = r".\plugins\JP_Lang_Pack\data"

def get_files(directory):
    file_paths = []
    for root, dirs, files in os.walk(directory):
        for f in files:
            if f.endswith('.csv') or f.endswith('.json'):
                rel_path = os.path.relpath(os.path.join(root, f), directory)
                file_paths.append(rel_path)
    return file_paths

core_files = set(get_files(core_dir))
plugin_files = set(get_files(plugin_dir))

missing_in_plugin = core_files - plugin_files

print(f"Total CSV/JSON files in Core: {len(core_files)}")
print(f"Total CSV/JSON files in Plugin: {len(plugin_files)}")

# Also print out the plugin files to see what IS currently being translated
print("\nFiles currently in Plugin:")
for f in sorted(list(plugin_files)):
    print(f"  - {f}")

# Find potentially interesting files missing in the plugin
interesting_keywords = ['rules', 'strings', 'descriptions', 'groups', 'hullplugins', 'skills', 'weapons', 'ships', 'names']
interesting_missing = []
for f in missing_in_plugin:
    if any(k in f.lower() for k in interesting_keywords):
        interesting_missing.append(f)

print(f"\nMissing files containing potential text ({len(interesting_missing)}):")
for f in sorted(interesting_missing)[:20]:
    print(f"  - {f}")
if len(interesting_missing) > 20:
    print("  - ... (truncated)")
