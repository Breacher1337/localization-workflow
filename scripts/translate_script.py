import urllib.request
import urllib.parse
import json
import codecs
import time
import os

def translate_batch(texts):
    if not texts: return []
    # Replace newlines so they don't break our batch delimiter
    safe_texts = [t.replace('\n', ' <BR> ') for t in texts]
    combined = "\n".join(safe_texts)
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=' + urllib.parse.quote(combined)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read().decode())
            translated = "".join(x[0] for x in result[0] if x[0])
            res_lines = translated.split('\n')
            if len(res_lines) == len(texts):
                return [x.replace(' <BR> ', '\n').replace('<BR>', '\n').replace(' <br> ', '\n').replace('<br>', '\n').strip() for x in res_lines]
            else:
                print(f"Line count mismatch: {len(res_lines)} vs {len(texts)}")
    except Exception as e:
        print("Batch error:", e)
    
    # Fallback 1 by 1
    res = []
    for t in safe_texts:
        url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=' + urllib.parse.quote(t)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode())
                translated = "".join(x[0] for x in result[0] if x[0])
                res.append(translated.replace(' <BR> ', '\n').replace('<BR>', '\n').replace(' <br> ', '\n').replace('<br>', '\n').strip())
            time.sleep(0.1)
        except Exception as e:
            print("Fallback error on", t, e)
            res.append(t.replace(' <BR> ', '\n'))
    return res

for i in range(4, 16):
    in_file = f'phase6_csv_chunk_{i}.json'
    out_file = f'phase6_csv_chunk_{i}_ja.json'
    if not os.path.exists(in_file):
        continue
    print(f"Processing {in_file}...")
    with codecs.open(in_file, 'r', 'utf-8') as f:
        data = json.load(f)
    
    keys = list(data.keys())
    values = [data[k] for k in keys]
    
    translated_values = []
    batch_size = 20
    for j in range(0, len(values), batch_size):
        batch = values[j:j+batch_size]
        translated_values.extend(translate_batch(batch))
        time.sleep(0.2)
    
    # map back
    out_data = {}
    for k, v in zip(keys, translated_values):
        out_data[k] = v
        
    with codecs.open(out_file, 'w', 'utf-8') as f:
        json.dump(out_data, f, ensure_ascii=False, indent=4)
    print(f"Saved {out_file}.")
