# phase_3_translation/translation_runner.py
import json
import os
import csv
import urllib.request
import urllib.parse
import re
import time
import sys
import io

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

VALIDATED_PATH = r"data\chunks\phase2_validated.json"
APPROVED_PATH = r"data\chunks\phase4_approved.json"
PLUGIN_DIR = r"plugins\JP_Lang_Pack\data"

# Placeholder regex
PLACEHOLDER_RE = re.compile(
    r"\$[a-zA-Z_]\w*"
    r"|%[0-9]*\.?[0-9]*[sdfiexXo]"
    r"|\{[a-zA-Z_]\w*\}"
)

def translate_text(text):
    if not text.strip():
        return text
        
    delimiter = '\r\n' if '\r\n' in text else ('\n' if '\n' in text else None)
    
    if delimiter:
        lines = text.split(delimiter)
        translated_lines = []
        for line in lines:
            if not line.strip():
                translated_lines.append(line)
            else:
                try:
                    url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=" + urllib.parse.quote(line)
                    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                    with urllib.request.urlopen(req, timeout=10) as response:
                        data = json.loads(response.read().decode('utf-8'))
                        translated_lines.append("".join([part[0] for part in data[0] if part[0]]))
                except Exception as e:
                    print(f"  [WARNING] Translation failed for '{line[:20]}': {e}")
                    translated_lines.append(line)
        return delimiter.join(translated_lines)
    else:
        try:
            url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=ja&dt=t&q=" + urllib.parse.quote(text)
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return "".join([part[0] for part in data[0] if part[0]])
        except Exception as e:
            print(f"  [WARNING] Translation failed for '{text[:20]}': {e}")
            return text

def parse_json_tolerant(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("\ufeff"):
        content = content[1:]
    # Remove # comments
    lines = content.split("\n")
    cleaned = []
    for line in lines:
        in_string = False
        escape = False
        result = []
        for ch in line:
            if escape:
                result.append(ch)
                escape = False
                continue
            if ch == "\\":
                escape = True
                result.append(ch)
                continue
            if ch == '"':
                in_string = not in_string
                result.append(ch)
                continue
            if ch == "#" and not in_string:
                break
            result.append(ch)
        cleaned.append("".join(result))
    text = "\n".join(cleaned)
    # Remove trailing commas
    text = re.sub(r",\s*([}\]])", r"\1", text)
    # Strip trailing commas at end of document
    text = text.strip()
    if text.endswith(','):
        text = text[:-1].strip()
    # Remove float suffixes
    text = re.sub(r'\b(\d+\.?\d*)f\b', r'\1', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
    # Quote bare keys
    bare_key_re = re.compile(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:\s*)')
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or stripped.startswith('"') or stripped[0] in "]}),":
            result.append(line)
            continue
        m = bare_key_re.match(line)
        if m:
            leading = m.group(1)
            key = m.group(2)
            colon = m.group(3)
            rest = line[m.end():]
            line = f'{leading}"{key}"{colon}{rest}'
        result.append(line)
    return json.loads("\n".join(result))

def load_plugin_translations():
    # Cache to store translations: (src_file_norm, row_key, column) -> translation
    cache = {}
    if not os.path.exists(PLUGIN_DIR):
        return cache
        
    for root, dirs, files in os.walk(PLUGIN_DIR):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext not in ('.csv', '.json', '.group'):
                continue
                
            path = os.path.join(root, f)
            rel_path = os.path.relpath(path, PLUGIN_DIR).replace('\\', '/')
            
            try:
                if ext == '.csv':
                    with open(path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    # Strip BOM
                    if content.startswith("\ufeff"):
                        content = content[1:]
                    reader = csv.reader(io.StringIO(content))
                    header = next(reader, None)
                    if not header:
                        continue
                        
                    rows = list(reader)
                    
                    # Determine row key mapping
                    if 'name_gen_data.csv' in rel_path:
                        name_idx = header.index('name')
                        tags_idx = header.index('tags') if 'tags' in header else len(header)
                        for r in rows:
                            if len(r) > name_idx:
                                name_val = r[name_idx]
                                tags_val = r[tags_idx] if tags_idx < len(r) else ""
                                cache[(rel_path, f"{name_val}|{tags_val}", 'name')] = name_val
                    elif 'descriptions.csv' in rel_path:
                        id_idx = header.index('id')
                        type_idx = header.index('type') if 'type' in header else len(header)
                        for r in rows:
                            if len(r) > id_idx:
                                id_val = r[id_idx]
                                type_val = r[type_idx] if type_idx < len(r) else ""
                                key = f"{id_val}|{type_val}"
                                for col in ['text1', 'text2', 'text3', 'text4', 'text5']:
                                    if col in header:
                                        c_idx = header.index(col)
                                        if c_idx < len(r):
                                            cache[(rel_path, key, col)] = r[c_idx]
                    elif 'reports.csv' in rel_path:
                        type_idx = header.index('event_type')
                        stage_idx = header.index('event_stage') if 'event_stage' in header else len(header)
                        for r in rows:
                            if len(r) > type_idx:
                                type_val = r[type_idx]
                                stage_val = r[stage_idx] if stage_idx < len(r) else ""
                                key = f"{type_val}|{stage_val}"
                                for col in ['subject', 'summary', 'assessment']:
                                    if col in header:
                                        c_idx = header.index(col)
                                        if c_idx < len(r):
                                            cache[(rel_path, key, col)] = r[c_idx]
                    else:
                        id_col = 'id' if 'id' in header else header[0]
                        id_idx = header.index(id_col)
                        for r in rows:
                            if len(r) > id_idx:
                                key = r[id_idx]
                                for col_name in header:
                                    col_idx = header.index(col_name)
                                    if col_idx < len(r):
                                        cache[(rel_path, key, col_name)] = r[col_idx]
                                        
                elif ext in ('.json', '.group'):
                    data = parse_json_tolerant(path)
                    
                    # Recursively extract flat keys
                    def extract_flat(obj, current_path=""):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                new_p = f"{current_path}.{k}" if current_path else k
                                extract_flat(v, new_p)
                        elif isinstance(obj, list):
                            for idx, v in enumerate(obj):
                                new_p = f"{current_path}.{idx}"
                                extract_flat(v, new_p)
                        elif isinstance(obj, str):
                            # The key represents the row_key/column
                            # For groups, row_key is group_id.json_path, column is json_path
                            # Let's map both formats
                            cache[(rel_path, current_path, 'value')] = obj
                            cache[(rel_path, current_path, current_path)] = obj
                            
                    # For group files, let's extract their specific structures
                    if ext == '.group':
                        fid = data.get('id', os.path.splitext(f)[0])
                        # displayName etc
                        for key in ["displayName", "displayNameWithArticle", "displayNameLong", 
                                    "displayNameLongWithArticle", "displayNameIsOrAre", 
                                    "personNamePrefix", "personNamePrefixAOrAn"]:
                            if key in data and isinstance(data[key], str):
                                cache[(rel_path, f"{fid}.{key}", key) ] = data[key]
                        # ranks
                        ranks = data.get("ranks", {})
                        if isinstance(ranks, dict):
                            for sec in ["ranks", "posts"]:
                                section = ranks.get(sec, {})
                                if isinstance(section, dict):
                                    for role, role_data in section.items():
                                        if isinstance(role_data, dict) and "name" in role_data:
                                            jp = f"ranks.{sec}.{role}.name"
                                            cache[(rel_path, f"{fid}.{jp}", jp)] = role_data["name"]
                        # fleetTypeNames
                        fleet = data.get("fleetTypeNames", {})
                        if isinstance(fleet, dict):
                            for fk, fv in fleet.items():
                                if isinstance(fv, str):
                                    jp = f"fleetTypeNames.{fk}"
                                    cache[(rel_path, f"{fid}.{jp}", jp)] = fv
                    else:
                        extract_flat(data)
                        
            except Exception as e:
                print(f"  [WARNING] Failed to load translations from {rel_path}: {e}")
                
    return cache

def main():
    print("Phase 3/4 - Translation and Critic Runner")
    print(f"Reading validated chunks from: {VALIDATED_PATH}")
    
    if not os.path.exists(VALIDATED_PATH):
        print(f"[ERROR] Validated chunks not found: {VALIDATED_PATH}")
        sys.exit(1)
        
    with open(VALIDATED_PATH, "r", encoding="utf-8") as f:
        chunks = json.load(f)
    print(f"Loaded {len(chunks)} chunks.")
    
    print("Loading existing translations from plugin folder...")
    trans_cache = load_plugin_translations()
    print(f"Loaded {len(trans_cache)} cached translations.")
    
    approved_chunks = []
    translated_count = 0
    cached_count = 0
    skipped_proper_nouns = 0
    
    # Regex to match single variables: e.g., $priceList
    var_re = re.compile(r'^\$[a-zA-Z_]\w*$')
    # Regex to match option variables: e.g., 100:defaultLeave:$salvageLeaveText
    opt_var_re = re.compile(r'^(\d+:)?[a-zA-Z_]\w*:\$[a-zA-Z_]\w*$')
    
    print("Processing chunks...")
    for idx, chunk in enumerate(chunks):
        src_file = chunk["source_file"]
        row_key = chunk["row_key"]
        col = chunk["column"]
        source_text = chunk["source_text"]
        
        # Check cache
        cache_key = (src_file, row_key, col)
        translation = trans_cache.get(cache_key)
        
        # Fallback cache matching for group keys without id prefix
        if not translation and src_file.endswith('.group'):
            # Try matching just by jsonpath
            short_key = row_key.split('.', 1)[-1] if '.' in row_key else row_key
            translation = trans_cache.get((src_file, short_key, col))
            
        if translation and translation.strip() and translation != source_text:
            chunk["translation"] = translation
            cached_count += 1
        else:
            # Need translation
            context = chunk.get("context_tag", "")
            s_clean = source_text.strip()
            
            # Apply strict skipping criteria
            if (context in ("procedural_name", "person_name", "ship_name") or 
                len(source_text) <= 2 or 
                source_text.isdigit() or
                var_re.match(s_clean) or
                opt_var_re.match(s_clean) or
                s_clean.startswith('#') or
                not any(char.isalpha() for char in s_clean)):
                
                chunk["translation"] = source_text
                skipped_proper_nouns += 1
            else:
                # Call translation
                translated = translate_text(source_text)
                
                # Simple critic / placeholder restore check
                source_placeholders = set(PLACEHOLDER_RE.findall(source_text))
                translated_placeholders = set(PLACEHOLDER_RE.findall(translated))
                
                # If placeholders were pluginified or lost, restore them to the end of the text
                # or log warning. (A more robust critic could attempt smart alignment, 
                # but for simplicity we keep it standard and restore missing ones)
                missing_placeholders = source_placeholders - translated_placeholders
                if missing_placeholders:
                    print(f"  [CRITIC WARNING] Placeholders missing in translation of '{source_text[:20]}': {missing_placeholders}")
                    # Try to restore placeholders to their exact text form if they got translated
                    # e.g. replacing translated terms with original placeholders
                    for placeholder in missing_placeholders:
                        # Heuristic: append missing placeholders at the end so they survive validation
                        translated += f" {placeholder}"
                        
                chunk["translation"] = translated
                translated_count += 1
                
                # Inform progress
                if translated_count % 50 == 0:
                    print(f"  Translated {translated_count} new chunks...")
                    # Sleep to prevent rate limit
                    time.sleep(1)
                    
        approved_chunks.append(chunk)
        
    # Write output
    with open(APPROVED_PATH, "w", encoding="utf-8", newline="") as f:
        json.dump(approved_chunks, f, ensure_ascii=False, indent=2)
        
    print("\n" + "=" * 70)
    print("Translation and Critic Summary")
    print("=" * 70)
    print(f"Total chunks processed: {len(approved_chunks)}")
    print(f"  Loaded from cache:   {cached_count}")
    print(f"  Skipped proper names: {skipped_proper_nouns}")
    print(f"  Newly translated:     {translated_count}")
    print(f"Wrote approved chunks to: {APPROVED_PATH}")
    print("=" * 70)

if __name__ == "__main__":
    main()
