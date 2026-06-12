import sys
import os
import config
﻿import os

plugin_dir = config.APPLICATION_CORE_DIR

for root, dirs, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith(('.csv', '.json')):
            path = os.path.join(root, f)
            with open(path, 'rb') as file:
                content = file.read()
            if content.startswith(b'\xef\xbb\xbf'):
                print(f"Removing BOM from {path}")
                with open(path, 'wb') as file:
                    file.write(content[3:])
