import sys
try:
    import hjson
except ImportError:
    print("hjson not found")
    sys.exit(1)

files = ['ship_names_ja.json', 'strings_ja.json']
for f in files:
    try:
        with open(f, 'r', encoding='utf-8') as file:
            hjson.load(file)
            print(f"{f} parsed successfully with hjson.")
    except Exception as e:
        print(f"Error parsing {f} with hjson: {e}")
