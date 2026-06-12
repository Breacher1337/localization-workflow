import os

workspace = r"."
files = os.listdir(workspace)

chunks = []
for f in files:
    if f.startswith("rules_complex_chunk_") and f.endswith(".json") and not f.endswith("_ja.json"):
        chunks.append(f)

missing = []
for c in chunks:
    ja_file = c.replace(".json", "_ja.json")
    if ja_file not in files:
        missing.append(c)

print(f"Total chunks: {len(chunks)}")
print(f"Missing _ja files: {missing}")

for c in chunks:
    ja_file = c.replace(".json", "_ja.json")
    if ja_file in files:
        # Check if it's an empty or identical file
        with open(os.path.join(workspace, c), 'r', encoding='utf-8') as f1:
            c1 = f1.read()
        with open(os.path.join(workspace, ja_file), 'r', encoding='utf-8') as f2:
            c2 = f2.read()
        if c1 == c2:
            missing.append(c) # Untranslated!
            print(f"Chunk {c} _ja file is identical to original (NOT TRANSLATED)")

print(f"Actually missing/untranslated: {missing}")
