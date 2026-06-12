import json
from deep_translator import GoogleTranslator

def translate_simple():
    print("Loading rules_simple.json...")
    with open('rules_simple.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    translator = GoogleTranslator(source='en', target='ja')
    translated_data = {}
    
    total = len(data)
    print(f"Translating {total} entries...")
    
    for i, (key, text) in enumerate(data.items()):
        try:
            ja_text = translator.translate(text)
            translated_data[key] = ja_text
        except Exception as e:
            print(f"Failed to translate {key}: {e}")
            translated_data[key] = text
            
        if (i+1) % 100 == 0:
            print(f"Progress: {i+1}/{total}")
            
    with open('rules_simple_translated.json', 'w', encoding='utf-8') as f:
        json.dump(translated_data, f, indent=4, ensure_ascii=False)
        
    print("Done! Saved to rules_simple_translated.json.")

if __name__ == '__main__':
    translate_simple()
