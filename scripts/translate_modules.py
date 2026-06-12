import os
import re
import codecs
import json
import urllib.request
import urllib.parse
import time

glossary = {}
with codecs.open('localization_tracking/master_glossary.csv', 'r', 'utf-8', errors='ignore') as f:
    for line in f:
        parts = line.split(',')
        if len(parts) >= 2:
            eng = parts[0].strip()
            jp = parts[1].strip()
            if eng and jp:
                glossary[eng] = jp

def translate_text(t):
    if t in glossary: return glossary[t]
    if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', t): return t
    url = 'https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=' + urllib.parse.quote(t)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            translated = "".join(x[0] for x in res[0] if x[0])
            time.sleep(0.1)
            return translated.strip()
    except Exception as e:
        return t

groups_dir = r'plugins\JP_Lang_Pack\data\world\groups'
group_files = [f for f in os.listdir(groups_dir) if f.endswith('.group')]

target_keys = {"displayName", "displayNameWithArticle", "displayNameLong", "displayNameLongWithArticle", "personNamePrefix", "name"}

def replacer(match):
    key = match.group(1)
    val = match.group(2)
    if key in target_keys:
        return f'"{key}":"{translate_text(val)}"'
    return match.group(0)

def replacer_fleet(match):
    key = match.group(1)
    val = match.group(2)
    return f'"{key}":"{translate_text(val)}"'

for file in group_files:
    path = os.path.join(groups_dir, file)
    with codecs.open(path, 'r', 'utf-8', errors='ignore') as f:
        content = f.read()
    
    # Replace targeted keys globally
    content = re.sub(r'"(displayName|displayNameWithArticle|displayNameLong|displayNameLongWithArticle|personNamePrefix|name)"\s*:\s*"([^"]+)"', replacer, content)
    
    # Replace fleetTypeNames block
    fleet_match = re.search(r'"fleetTypeNames"\s*:\s*\{([^}]+)\}', content)
    if fleet_match:
        old_block = fleet_match.group(1)
        new_block = re.sub(r'"([^"]+)"\s*:\s*"([^"]+)"', replacer_fleet, old_block)
        content = content[:fleet_match.start(1)] + new_block + content[fleet_match.end(1):]
        
    with codecs.open(path, 'w', 'utf-8') as f:
        f.write(content)
    print("Processed", file)

print("Done processing group files!")
