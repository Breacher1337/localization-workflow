import sys
import os
import config
﻿import os

target_dir = config.APPLICATION_CORE_DIR
query = "Open a comm link"

found = False
for root, dirs, files in os.walk(target_dir):
    for f in files:
        if f.endswith(('.csv', '.json', '.java', '.txt', '.txt.po', '.json.po')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    content = file.read()
                    if query in content:
                        print(f"Found in {path}")
                        found = True
            except:
                pass
if not found:
    print("Not found anywhere in text files.")
