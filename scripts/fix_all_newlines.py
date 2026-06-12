import os
import csv

plugin_dir = r'.\plugins\JP_Lang_Pack\data'

files_fixed = 0
cells_fixed = 0

for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv') and f != 'rules.csv':
            plugin_path = os.path.join(root, f)
            
            with open(plugin_path, 'r', encoding='utf-8') as file:
                reader = list(csv.reader(file))
                
            file_changed = False
            for r in reader:
                for i in range(len(r)):
                    if '\\n' in r[i]:
                        r[i] = r[i].replace('\\n', '\n')
                        file_changed = True
                        cells_fixed += 1
                        
            if file_changed:
                with open(plugin_path, 'w', encoding='utf-8', newline='') as file:
                    writer = csv.writer(file, lineterminator='\r\n')
                    writer.writerows(reader)
                files_fixed += 1
                print(f'Fixed newlines in {os.path.relpath(plugin_path, plugin_dir)}')

print(f'Done! Fixed {cells_fixed} cells across {files_fixed} CSV files.')
