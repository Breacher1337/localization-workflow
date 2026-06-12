import os
import csv

plugin_dir = r".\plugins\JP_Lang_Pack\data"

for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv'):
            path = os.path.join(root, f)
            try:
                fixed_rows = []
                with open(path, 'r', encoding='utf-8', errors='ignore') as f_obj:
                    reader = csv.reader(f_obj)
                    for row in reader:
                        # Restore literal '\n' back into actual newlines (Unix \n)
                        # csv.writer with lineterminator='\r\n' will output standard CSV
                        # where actual newlines inside cells are preserved correctly within quotes.
                        new_row = [cell.replace('\\n', '\n') for cell in row]
                        fixed_rows.append(new_row)
                        
                with open(path, 'w', encoding='utf-8', newline='') as f_obj:
                    # using standard csv writer
                    writer = csv.writer(f_obj, lineterminator='\r\n')
                    writer.writerows(fixed_rows)
            except Exception as e:
                print(f"Error restoring {f}: {e}")

print("Restored actual newlines inside CSV cells!")
