import csv, re

path = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

with open(path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    text_idx = header.index('text')
    
    matches = []
    for i, row in enumerate(reader):
        text = row[text_idx]
        if re.search(r'(?i)\bping\b', text) or re.search(r'(?i)\bcorporation\b', text) or 'TriiPad' in text or 'Tripad' in text:
            matches.append((i, text))

with open(r'.\matches.txt', 'w', encoding='utf-8') as f_out:
    for i, text in matches:
        f_out.write(f'Row {i}: {text}\n')
        
print(f'Found {len(matches)} matches. See matches.txt')
