import csv

plugin_file = r"e:\lamesa\2026\application-jp\plugins\JP_Lang_Pack\data\campaign\rules.csv"

try:
    with open(plugin_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i >= 900 and i <= 915:
                # Just loop through to catch parsing errors
                pass
            if i > 915:
                break
    print("CSV parsed successfully up to line 915")
except Exception as e:
    print(f"Error parsing at line {reader.line_num}: {e}")
