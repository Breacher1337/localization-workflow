import sys
import os
import config
﻿import csv
import sys
import os

plugin_dir = config.APPLICATION_CORE_DIR
input_csv = r".\descriptions_translated.csv"
output_csv = os.path.join(plugin_dir, "descriptions.csv")

try:
    with open(input_csv, 'r', encoding='utf-8') as fin, open(output_csv, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        
        for row in reader:
            if not row: continue
            if len(row) > 0 and row[0].strip() == "":
                # Skip empty ID rows
                continue
            writer.writerow(row)
            
    print(f"Successfully cleaned and copied descriptions.csv to {output_csv}")
except Exception as e:
    print(f"Error: {e}")
