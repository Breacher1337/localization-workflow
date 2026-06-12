import os
import csv

plugin_dir = r".\plugins\JP_Lang_Pack\data"

for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as f_obj:
                    content = f_obj.read()
                    
                # We can check if there are multi-line fields by reading with csv pluginule
                with open(path, 'r', encoding='utf-8') as f_obj:
                    reader = csv.reader(f_obj)
                    for i, row in enumerate(reader):
                        for cell in row:
                            if '\n' in cell:
                                print(f"WARNING: File {f} has an embedded newline in row {i}!")
                                break
            except Exception as e:
                print(f"Error checking {f}: {e}")
