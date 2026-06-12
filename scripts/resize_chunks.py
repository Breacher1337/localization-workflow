import json
import os
import glob

# delete large chunks
for f in glob.glob(r".\phase6_large_chunk_*.json"):
    os.remove(f)

all_data = {}
for i in range(101):
    path = fr".\phase6_csv_chunk_{i}.json"
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            all_data.update(json.load(f))

keys = list(all_data.keys())
chunk_size = 100
total_chunks = (len(keys) // chunk_size) + 1

for i in range(total_chunks):
    chunk_keys = keys[i*chunk_size : (i+1)*chunk_size]
    if not chunk_keys: continue
    chunk_dict = {k: all_data[k] for k in chunk_keys}
    
    out_path = fr".\phase6_csv_chunk_{i}.json"
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(chunk_dict, f, indent=4, ensure_ascii=False)

print(f"Resized into {total_chunks} chunks of 100 items each.")
