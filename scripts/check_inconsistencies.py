import os
import re

plugin_dir = r".\plugins\JP_Lang_Pack\data"

targets = {
    "Independent_Bad": r"独立した",
    "Luddic_Variations": r"ルディック|ルゥディック|ラディック|ルッディック",
    "Hegemony_Bad": r"覇権"
}

results = {k: 0 for k in targets}

for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv') or f.endswith('.json') or f.endswith('.group'):
            path = os.path.join(root, f)
            try:
                with open(path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    for key, pattern in targets.items():
                        matches = len(re.findall(pattern, content))
                        results[key] += matches
            except Exception as e:
                pass

for k, v in results.items():
    print(f"{k}: {v} matches found")
