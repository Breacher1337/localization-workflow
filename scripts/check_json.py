import json
import sys

files = ['ship_names_ja.json', 'strings_ja.json']
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            json.load(file)
            print(f"{f} parsed successfully.")
    except Exception as e:
        print(f"Error parsing {f}: {e}")
