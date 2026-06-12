import os
import csv

def compile_ui():
    out_file = 'ui.csv'
    with open(out_file, 'w', encoding='utf-8', newline='') as fout:
        writer = csv.writer(fout)
        writer.writerow(['English Source', 'Japanese Translation'])
        
        for i in range(1, 9):
            in_file = f'chunk_{i}_translated.csv'
            if os.path.exists(in_file):
                print(f"Reading {in_file}...")
                with open(in_file, 'r', encoding='utf-8') as fin:
                    reader = csv.reader(fin)
                    for row in reader:
                        if len(row) >= 2:
                            writer.writerow([row[0], row[1]])
            else:
                print(f"Warning: {in_file} not found!")

if __name__ == '__main__':
    compile_ui()
    print("UI Compilation complete.")
