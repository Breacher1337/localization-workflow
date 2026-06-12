import re

def fix_chunk(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    out = f"\n--- {path} ---\n"
    for i in range(len(lines)):
        if "chunk_15" in path and 90 <= i+1 <= 96:
            out += f"{i+1}: {lines[i]}\n"
        if "chunk_38" in path and 41 <= i+1 <= 47:
            out += f"{i+1}: {lines[i]}\n"
    
    with open("json_errors.txt", "a", encoding="utf-8") as f:
        f.write(out)

with open("json_errors.txt", "w", encoding="utf-8") as f:
    f.write("")

fix_chunk(r".\options_chunk_15_ja.json")
fix_chunk(r".\options_chunk_38_ja.json")
