import sys
import os
import config
import csv
import json
import os

def merge_rules():
    rules_path = config.APPLICATION_CORE_DIR
    output_path = r".\localization_tracking\rules_translated.csv"
    
    # Increase CSV field size limit
    csv.field_size_limit(10000000)
    
    translated_texts = {}
    
    # Load simple translations
    simple_path = r".\rules_simple_translated.json"
    if os.path.exists(simple_path):
        with open(simple_path, 'r', encoding='utf-8') as f:
            simple_data = json.load(f)
            # Keys in JSON are strings, convert to int
            for k, v in simple_data.items():
                translated_texts[int(k)] = v
                
    # Load complex chunks
    for i in range(57):
        chunk_path = fr".\rules_complex_chunk_{i}_ja.json"
        if os.path.exists(chunk_path):
            with open(chunk_path, 'r', encoding='utf-8') as f:
                chunk_data = json.load(f)
                for k, v in chunk_data.items():
                    translated_texts[int(k)] = v
        else:
            print(f"Warning: Chunk {i} is missing!")
            
    print(f"Loaded {len(translated_texts)} translated text strings.")
    
    # Process original rules.csv
    with open(rules_path, 'r', encoding='cp1252') as f_in:
        reader = csv.reader(f_in)
        header = next(reader)
        
        # Find the index of the 'text' column
        try:
            text_idx = header.index('text')
        except ValueError:
            print("Error: 'text' column not found in rules.csv")
            return
            
        with open(output_path, 'w', encoding='utf-8', newline='') as f_out:
            writer = csv.writer(f_out)
            writer.writerow(header)
            
            replaced_count = 0
            for row_idx, row in enumerate(reader):
                if row_idx in translated_texts:
                    # Update text
                    row[text_idx] = translated_texts[row_idx]
                    replaced_count += 1
                writer.writerow(row)
                
    print(f"Successfully replaced {replaced_count} lines in {output_path}")

if __name__ == '__main__':
    merge_rules()
