import os

plugin_path = r".\plugins\JP_Lang_Pack\data\campaign\abilities.csv"

with open(plugin_path, 'rb') as f:
    header = f.read(10)
    print(f"First 10 bytes: {header}")
    if header.startswith(b'\xef\xbb\xbf'):
        print("ERROR: BOM DETECTED!")
    else:
        print("SUCCESS: No BOM detected.")
