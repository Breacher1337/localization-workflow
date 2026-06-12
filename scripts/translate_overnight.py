import json
import re
import csv
import os
import time
from deep_translator import GoogleTranslator

def load_glossary():
    glossary = []
    path = r".\localization_tracking\master_glossary.csv"
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            en = row['English Source'].strip()
            ja = row['Japanese Translation'].strip()
            # Sort by length descending so "Luddic Path" is replaced before "Luddic"
            if en and ja:
                glossary.append((en, ja))
    glossary.sort(key=lambda x: len(x[0]), reverse=True)
    return glossary

def translate_chunk(chunk_id, glossary, translator):
    filename = f"rules_complex_chunk_{chunk_id}.json"
    out_filename = f"rules_complex_chunk_{chunk_id}_ja.json"
    
    if os.path.exists(out_filename):
        print(f"Chunk {chunk_id} already translated. Skipping.")
        return
        
    path = os.path.join(r".", filename)
    if not os.path.exists(path):
        return
        
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    translated_data = {}
    print(f"Translating chunk {chunk_id} ({len(data)} items)...", flush=True)
    
    item_counter = 0
    
    for key, text in data.items():
        original_text = text
        
        # 1. Protect variables like $playerName
        var_map = {}
        var_counter = 0
        
        # Find all $vars
        for match in re.finditer(r'\$[a-zA-Z0-9_\.]+', text):
            var_str = match.group(0)
            if var_str not in var_map.values():
                placeholder = f"_V{var_counter}_"
                var_map[placeholder] = var_str
                text = text.replace(var_str, placeholder)
                var_counter += 1
                
        # 2. Protect glossary terms
        glos_map = {}
        glos_counter = 0
        for en_term, ja_term in glossary:
            # simple word boundary replacement
            pattern = r'\b' + re.escape(en_term) + r'\b'
            if re.search(pattern, text, flags=re.IGNORECASE):
                placeholder = f"_G{glos_counter}_"
                glos_map[placeholder] = ja_term
                text = re.sub(pattern, placeholder, text, flags=re.IGNORECASE)
                glos_counter += 1
                
        # 3. Translate
        try:
            # Google Translate handles up to 5000 chars, chunks should be small
            ja_text = translator.translate(text)
        except Exception as e:
            print(f"Error translating {key}: {e}")
            ja_text = text
            time.sleep(2) # Backoff
            
        # 4. Restore placeholders
        for ph, ja_term in glos_map.items():
            ja_text = ja_text.replace(ph, ja_term)
            # Sometimes spaces are added around it
            ja_text = ja_text.replace(f"{ph} ", ja_term).replace(f" {ph}", ja_term)
            
        for ph, var_term in var_map.items():
            ja_text = ja_text.replace(ph, var_term)
            ja_text = ja_text.replace(f"{ph} ", var_term).replace(f" {ph}", var_term)
            
        translated_data[key] = ja_text
        item_counter += 1
        if item_counter % 10 == 0:
            print(f"  ...translated {item_counter}/{len(data)} items in chunk {chunk_id}.", flush=True)
        
    with open(out_filename, 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, indent=4, ensure_ascii=False)
        
    print(f"Chunk {chunk_id} complete.", flush=True)

def main():
    glossary = load_glossary()
    translator = GoogleTranslator(source='en', target='ja')
    
    # Missing chunks are 8, 12, 13..56
    chunks_to_do = [8, 12] + list(range(13, 57))
    
    for chunk_id in chunks_to_do:
        translate_chunk(chunk_id, glossary, translator)
        time.sleep(1) # Small delay between chunks

if __name__ == '__main__':
    main()
