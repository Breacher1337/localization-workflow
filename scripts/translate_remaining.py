import json
import csv
import time
from deep_translator import GoogleTranslator

translator = GoogleTranslator(source='en', target='ja')

def translate_csv(in_file, out_file):
    print(f"Translating {in_file}...")
    with open(in_file, 'r', encoding='utf-8') as fin, open(out_file, 'w', encoding='utf-8', newline='') as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)
        for row in reader:
            if len(row) >= 2:
                key = row[0]
                val = row[1]
                if not val.strip():
                    writer.writerow([key, val])
                    continue
                try:
                    tval = translator.translate(val)
                    writer.writerow([key, tval])
                except Exception as e:
                    print(f"Error translating: {val} -> {e}")
                    writer.writerow([key, val])
                time.sleep(0.1)

def translate_json(in_file, out_file):
    print(f"Translating {in_file}...")
    with open(in_file, 'r', encoding='utf-8') as fin:
        data = json.load(fin)
    
    out_data = {}
    for text in data:
        if not text.strip():
            out_data[text] = text
            continue
        try:
            tval = translator.translate(text)
            out_data[text] = tval
        except Exception as e:
            print(f"Error translating: {text} -> {e}")
            out_data[text] = text
        time.sleep(0.1)
    
    with open(out_file, 'w', encoding='utf-8') as fout:
        json.dump(out_data, fout, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    translate_csv('chunk_6.csv', 'chunk_6_translated.csv')
    translate_json('desc_chunk_5.json', 'desc_chunk_5_ja.json')
    translate_json('desc_chunk_6.json', 'desc_chunk_6_ja.json')
    print("Done!")
