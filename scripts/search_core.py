import sys
import os
import config
﻿import os

target_dir = config.APPLICATION_CORE_DIR
query = "Open a comm link"

for root, dirs, files in os.walk(target_dir):
    for f in files:
        if f.endswith(('.csv', '.json', '.java', '.txt')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    for i, line in enumerate(file):
                        if query in line:
                            print(f"{path}:{i+1}: {line.strip()}")
            except:
                pass
