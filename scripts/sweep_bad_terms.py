"""Sweep all plugin files for any remaining bad terms."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
plugin = r'.\plugins\JP_Lang_Pack\data'
bad_terms = ['磁束', '流束', '光束', '艦艇', '独立した', '覇権', 'ルッダイト', 'トライタキオン', '家長世代', 'コントローラー全般', '戦闘準備状態']
found = False
for root, _, files in os.walk(plugin):
    for f in files:
        if f.endswith(('.csv','.json','.group')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            for term in bad_terms:
                count = content.count(term)
                if count > 0:
                    print(f'  WARNING: {f}: {count}x "{term}"')
                    found = True
if not found:
    print('  ALL CLEAN - No bad terms found in any plugin file!')
