import sys
import os
import config
import os
import shutil

def convert_to_utf8_bom(file_path):
    print(f"Adding BOM to {file_path}")
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Write back with utf-8 (which adds the BOM)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

if __name__ == '__main__':
    plugin_dir = config.APPLICATION_CORE_DIR
    
    files_to_convert = [
        "descriptions.csv",
        "strings.json",
        "ship_names.json"
    ]
    
    for fname in files_to_convert:
        fpath = os.path.join(plugin_dir, fname)
        if os.path.exists(fpath):
            convert_to_utf8_bom(fpath)
        else:
            print(f"Could not find {fpath}")
