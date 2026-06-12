import sys
import os
import config
import csv
import json
import re
import os

def prepare_rules():
    rules_path = config.APPLICATION_CORE_DIR
    
    simple_bucket = {}
    complex_bucket = {}
    
    # Increase CSV field size limit just in case
    csv.field_size_limit(10000000)
    
    with open(rules_path, 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f)
        for row_idx, row in enumerate(reader):
            text = row.get('text', '').strip()
            if not text:
                continue
                
            # Rule for complex: contains $variable or is very long (approximating 3 sentences)
            is_complex = False
            if '$' in text:
                is_complex = True
            elif len(text) > 150 or text.count('.') >= 3:
                is_complex = True
                
            if is_complex:
                complex_bucket[row_idx] = text
            else:
                simple_bucket[row_idx] = text

    print(f"Found {len(simple_bucket)} simple text rows.")
    print(f"Found {len(complex_bucket)} complex text rows.")
    
    with open('rules_simple.json', 'w', encoding='utf-8') as f:
        json.dump(simple_bucket, f, indent=4)
        
    with open('rules_complex.json', 'w', encoding='utf-8') as f:
        json.dump(complex_bucket, f, indent=4)
        
    # Split complex into chunks of 100
    chunk_size = 100
    complex_items = list(complex_bucket.items())
    num_chunks = (len(complex_items) + chunk_size - 1) // chunk_size
    
    for i in range(num_chunks):
        chunk_data = dict(complex_items[i*chunk_size : (i+1)*chunk_size])
        with open(f'rules_complex_chunk_{i}.json', 'w', encoding='utf-8') as f:
            json.dump(chunk_data, f, indent=4)
            
    print(f"Generated {num_chunks} complex chunks.")

if __name__ == '__main__':
    prepare_rules()
