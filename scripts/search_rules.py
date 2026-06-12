import sys
import os
import config
﻿import csv
with open(config.APPLICATION_CORE_DIR, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if len(row) > 4 and "Open a comm link" in row[4]:
            print(f"Row {i+1}: text = {row[4]}, options = {row[5]}")
        elif len(row) > 5 and "Open a comm link" in row[5]:
            print(f"Row {i+1}: text = {row[4]}, options = {row[5]}")
