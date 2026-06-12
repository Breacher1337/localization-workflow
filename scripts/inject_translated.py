import os
import json
import csv

def process_translated_chunks():
    plugin_dir = r'.\plugins\JP_Lang_Pack'
    
    # Load all translations from all 4 chunks
    translations = []
    for i in range(1, 5):
        chunk_file = f'.\\translation_chunk_{i}_translated.json'
        if os.path.exists(chunk_file):
            with open(chunk_file, 'r', encoding='utf-8') as f:
                translations.extend(json.load(f))
        else:
            print(f"Warning: {chunk_file} not found yet.")

    if not translations:
        print("No translations found.")
        return

    # Group by file to minimize I/O
    files_to_pluginify = {}
    for item in translations:
        if 'translated_text' not in item: continue
        file_path = item['file']
        if file_path not in files_to_pluginify:
            files_to_pluginify[file_path] = []
        files_to_pluginify[file_path].append(item)

    # Process each file
    for file_path, items in files_to_pluginify.items():
        if not os.path.exists(file_path):
            continue
            
        print(f"Pluginifying {file_path}")
        if file_path.endswith('.csv'):
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                
            for item in items:
                r = item['row_idx']
                c = item['col_idx']
                if r < len(rows) and c < len(rows[r]):
                    rows[r][c] = item['translated_text']
                    
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(rows)
                
        elif file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            for item in items:
                json_path = item['json_path']
                translated_text = item['translated_text']
                # Evaluate path and set value
                # e.g. path="['tags'][0]"
                exec(f"data{json_path} = {repr(translated_text)}")
                
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

    print("Finished injecting translations!")

if __name__ == "__main__":
    process_translated_chunks()
