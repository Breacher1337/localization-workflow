import json

plugin_path = r".\plugins\JP_Lang_Pack\data\strings\strings.json"

try:
    with open(plugin_path, 'r', encoding='utf-8') as f:
        data = f.read()
        lines = data.split('\n')
        for i, line in enumerate(lines):
            if "ongoingBattleShareIFF" in line or "You decide to" in line:
                print(f"Line {i+1}: {line.strip().encode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")
