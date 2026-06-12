import sys
import os
import config
﻿import os

plugin_dir = config.APPLICATION_CORE_DIR
bom = b'\xef\xbb\xbf'

count = 0
for root, dirs, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith(('.csv', '.json')):
            path = os.path.join(root, f)
            with open(path, 'rb') as file:
                content = file.read()
                if content.startswith(bom):
                    print(f"Found BOM in {path}")
                    count += 1
if count == 0:
    print("No BOMs found!")
