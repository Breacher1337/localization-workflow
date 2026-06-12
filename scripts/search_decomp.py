import os

target_dir = r".\decompiled_core"
query = "Open a comm link"

for root, dirs, files in os.walk(target_dir):
    for f in files:
        if f.endswith(('.java')):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                    for i, line in enumerate(file):
                        if query in line:
                            print(f"{f}:{i+1}: {line.strip()}")
            except:
                pass
