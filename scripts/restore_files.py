import sys
import os
import config
﻿import shutil
import os

plugin_dir = config.APPLICATION_CORE_DIR
src_dir = r"."

files_to_copy = {
    "descriptions_translated.csv": "descriptions.csv",
    "ship_names_ja.json": "ship_names.json",
    "strings_ja.json": "strings.json"
}

for src_name, dest_name in files_to_copy.items():
    src_path = os.path.join(src_dir, src_name)
    dest_path = os.path.join(plugin_dir, dest_name)
    if os.path.exists(src_path):
        print(f"Copying {src_name} to {dest_name}...")
        shutil.copy2(src_path, dest_path)
    else:
        print(f"Source {src_name} not found!")
