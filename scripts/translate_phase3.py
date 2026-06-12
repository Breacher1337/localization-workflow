import sys
import os
import config
﻿import hjson
import json
import csv
import os
import time
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='en', target='ja')

core_dir = config.APPLICATION_CORE_DIR
plugin_dir = config.APPLICATION_CORE_DIR

files_to_translate = [
    ('hullplugins', 'hull_plugins.csv', 'csv_complex'),
    ('strings', 'tips.json', 'json_list'),
    ('strings', 'tooltips.json', 'json_dict'),
    ('world/groups', 'default_ranks.json', 'json_dict'),
    ('world/groups', 'default_fleet_type_names.json', 'json_dict'),
    ('config', 'tag_data.json', 'json_dict')
]

def safe_translate(text):
    if not text or not str(text).strip(): return text
    if len(str(text)) < 2: return text
    try:
        res = translator.translate(text)
        return res if res else text
    except Exception as e:
        print(f"Error translating: {text[:30]}... {e}")
        time.sleep(2)
        return text

for folder, filename, fmt in files_to_translate:
    in_path = os.path.join(core_dir, folder, filename)
    out_folder = os.path.join(plugin_dir, folder)
    os.makedirs(out_folder, exist_ok=True)
    out_path = os.path.join(out_folder, filename)
    
    if os.path.exists(out_path) and os.path.getsize(out_path) > 100:
        if filename != 'hull_plugins.csv':
            print(f"Skipping {filename}, already exists.")
            continue
        
    print(f"Translating {filename}...")
    
    if fmt == 'csv_complex':
        with open(in_path, 'r', encoding='utf-8') as f:
            reader = list(csv.reader(f))
        
        headers = reader[0]
        name_idx = headers.index('name')
        desc_idx = headers.index('desc') if 'desc' in headers else -1
        short_idx = headers.index('short') if 'short' in headers else -1
        
        existing_rows = []
        if os.path.exists(out_path):
            with open(out_path, 'r', encoding='utf-8') as f:
                existing_rows = list(csv.reader(f))
        
        start_idx = len(existing_rows) if len(existing_rows) > 1 else 1
        
        with open(out_path, 'a' if start_idx > 1 else 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            if start_idx == 1:
                writer.writerow(headers)
                
            for row in reader[start_idx:]:
                if len(row) > name_idx and row[name_idx].strip():
                    row[name_idx] = safe_translate(row[name_idx])
                if desc_idx != -1 and len(row) > desc_idx and row[desc_idx].strip():
                    row[desc_idx] = safe_translate(row[desc_idx])
                if short_idx != -1 and len(row) > short_idx and row[short_idx].strip():
                    row[short_idx] = safe_translate(row[short_idx])
                writer.writerow(row)
                f.flush()
                
    elif fmt == 'json_list':
        with open(in_path, 'r', encoding='utf-8') as f:
            data = hjson.loads(f.read())
            
        if 'tips' in data:
            for i, item in enumerate(data['tips']):
                if isinstance(item, dict) and 'tip' in item:
                    item['tip'] = safe_translate(item['tip'])
                elif isinstance(item, str):
                    data['tips'][i] = safe_translate(item)
                    
        with open(out_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    elif fmt == 'json_dict':
        try:
            with open(in_path, 'r', encoding='utf-8') as f:
                data = hjson.loads(f.read())
                
            for k, v in data.items():
                if isinstance(v, str):
                    data[k] = safe_translate(v)
                elif isinstance(v, dict) and 'name' in v:
                    v['name'] = safe_translate(v['name'])
                    
            with open(out_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Could not parse {filename}: {e}")

print("Phase 3 translation complete!")
