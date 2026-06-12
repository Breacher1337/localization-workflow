import csv, re
from collections import Counter

path = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

words = Counter()
with open(path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    text_idx = header.index('text')
    
    for row in reader:
        text = row[text_idx]
        if not text: continue
        # Find all English words, ignore if they look like variables like $var or _V0_
        for w in re.findall(r'\b[A-Za-z]{3,}\b', text):
            if '$' not in text and w.lower() not in ['the', 'and', 'for', 'you', 'are', 'not']:
                words[w] += 1

print("Most common english words:")
for w, c in words.most_common(100):
    print(f"{w}: {c}")
