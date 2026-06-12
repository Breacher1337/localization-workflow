import csv
import re

plugin_path = r".\plugins\JP_Lang_Pack\data\strings\descriptions.csv"

def is_japanese(text):
    return bool(re.search(r'[あ-んア-ン一-龥]', text))

try:
    with open(plugin_path, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        total = 0
        translated = 0
        for row in reader:
            for col in ['text1', 'text2', 'text3', 'text4', 'text5']:
                if col in row and row[col].strip():
                    total += 1
                    if is_japanese(row[col]):
                        translated += 1
        print(f"descriptions.csv: {translated}/{total} strings translated.")
except Exception as e:
    print(f"Error: {e}")
