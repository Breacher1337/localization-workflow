import csv
import json
import math

def extract():
    texts = []
    with open('descriptions.csv', 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for key in ['text1', 'text2', 'text3']:
                if key in row and row[key].strip() != '':
                    texts.append(row[key])

    # Remove duplicates to save tokens
    unique_texts = list(set(texts))
    
    print(f"Found {len(unique_texts)} unique text blocks.")
    
    # Split into 6 chunks
    chunks = 6
    chunk_size = math.ceil(len(unique_texts) / chunks)
    
    for i in range(chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, len(unique_texts))
        if start >= end:
            break
        chunk_data = unique_texts[start:end]
        
        with open(f'desc_chunk_{i+1}.json', 'w', encoding='utf-8') as out:
            json.dump(chunk_data, out, indent=2, ensure_ascii=False)
            
        print(f"Wrote {len(chunk_data)} texts to desc_chunk_{i+1}.json")

if __name__ == "__main__":
    extract()
