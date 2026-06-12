"""Final sweep: fix all remaining bad terms across ALL plugin files."""
import os, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PLUGIN = r'.\plugins\JP_Lang_Pack\data'

fixes = [
    ("磁束", "フラックス"),
    ("家長世代", "氏族女家長"),
    ("戦闘準備状態", "戦闘準備態勢"),
    ("艦艇", "艦船"),
]

total = 0
for root, _, files in os.walk(PLUGIN):
    for f in files:
        if f.endswith(('.csv', '.json', '.group')):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8') as fh:
                content = fh.read()
            original = content
            file_count = 0
            for old, new in fixes:
                if old in content:
                    n = content.count(old)
                    content = content.replace(old, new)
                    file_count += n
                    print(f"  ✅ {f}: {old} → {new} ({n}x)")
            if content != original:
                with open(path, 'w', encoding='utf-8', newline='') as fh:
                    fh.write(content)
                total += file_count

print(f"\nFinal sweep: {total} replacements across all plugin files.")
