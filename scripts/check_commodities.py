import json
with open(r'.\phase6_csv_chunk_0_ja.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    found = 0
    for k, v in data.items():
        if 'compluginities.csv' in k:
            found += 1
            print(k, v)
    print(f"Found {found} compluginities keys.")
