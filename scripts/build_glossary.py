import sys
import os
import config
import os
import json
import re
import csv
from deep_translator import GoogleTranslator

def strip_comments(text):
    # Remove single line comments # and //
    text = re.sub(r'#.*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'//.*$', '', text, flags=re.MULTILINE)
    return text

def parse_loose_json(text):
    try:
        return json.loads(strip_comments(text).replace(',\n}', '\n}').replace(',\n]', '\n]'))
    except Exception as e:
        return None

def extract():
    groups_dir = config.APPLICATION_CORE_DIR
    starmap_path = config.APPLICATION_CORE_DIR
    
    extracted_terms = set()
    terms_list = []
    
    # 1. Starmap (Star Systems)
    if os.path.exists(starmap_path):
        with open(starmap_path, 'r', encoding='utf-8') as f:
            content = f.read()
            # Extract keys manually since starmap might have trailing commas
            for match in re.finditer(r'"([a-zA-Z0-9_\-]+)"\s*:', strip_comments(content)):
                system_name = match.group(1).replace('_', ' ').title()
                if system_name not in extracted_terms:
                    extracted_terms.add(system_name)
                    terms_list.append({'en': system_name, 'type': 'Map/System', 'context': 'Star system name'})
    
    # 2. Groups
    if os.path.exists(groups_dir):
        for fname in os.listdir(groups_dir):
            if fname.endswith('.group'):
                path = os.path.join(groups_dir, fname)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    # regex to find displayName
                    match = re.search(r'"displayName"\s*:\s*"([^"]+)"', content)
                    if match:
                        name = match.group(1)
                        if name not in extracted_terms:
                            extracted_terms.add(name)
                            terms_list.append({'en': name, 'type': 'Group', 'context': 'Group display name'})
                    
                    # regex to find ranks and posts names
                    for match in re.finditer(r'"name"\s*:\s*"([^"]+)"', content):
                        name = match.group(1)
                        # Filter out things that are too long
                        if len(name) < 30 and name not in extracted_terms:
                            extracted_terms.add(name)
                            terms_list.append({'en': name, 'type': 'Rank/Post', 'context': 'Character rank or post'})

    print(f"Extracted {len(terms_list)} terms. Translating...")
    
    translator = GoogleTranslator(source='en', target='ja')
    
    glossary_path = "localization_tracking/master_glossary.csv"
    existing_en = set()
    
    if os.path.exists(glossary_path):
        with open(glossary_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                existing_en.add(row['English Source'])
    
    new_rows = []
    for term in terms_list:
        if term['en'] not in existing_en:
            try:
                ja_translation = translator.translate(term['en'])
                new_rows.append({
                    'English Source': term['en'],
                    'Japanese Translation': ja_translation,
                    'Type': term['type'],
                    'Context & Localization Nuance': term['context'],
                    'Status': 'Auto-translated'
                })
                print(f"Translated: {term['en']} -> {ja_translation}")
            except Exception as e:
                print(f"Failed to translate {term['en']}: {e}")
                
    if new_rows:
        with open(glossary_path, 'a', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['English Source', 'Japanese Translation', 'Type', 'Context & Localization Nuance', 'Status'])
            # Only write header if file is totally empty
            if os.path.getsize(glossary_path) == 0:
                writer.writeheader()
            writer.writerows(new_rows)
        print(f"Added {len(new_rows)} new terms to master_glossary.csv.")
    else:
        print("No new terms to add.")

if __name__ == '__main__':
    extract()
