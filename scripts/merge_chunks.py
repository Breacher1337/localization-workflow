import json
import os

all_data = {}
for i in range(101):
    path = fr".\phase6_csv_chunk_{i}.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            all_data.update(json.load(f))
        os.remove(path)

keys = list(all_data.keys())
chunk_size = 500
total_chunks = (len(keys) // chunk_size) + 1

for i in range(total_chunks):
    chunk_keys = keys[i*chunk_size : (i+1)*chunk_size]
    if not chunk_keys: continue
    chunk_dict = {k: all_data[k] for k in chunk_keys}
    
    out_path = fr".\phase6_large_chunk_{i}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(chunk_dict, f, indent=4, ensure_ascii=False)

print(f"Merged into {total_chunks} large chunks.")
