# phase_3_translation/translation_runner.py
import json
import os
import csv
import re
import time
import sys
import io
import os

# Add the script's directory to sys.path so we can import local pluginules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

def mask_glossary(chunk):
    text = chunk["source_text"]
    glossary_hits = chunk.get("glossary_hits", [])
    if not glossary_hits:
        chunk["masked_text"] = text
        chunk["placeholders"] = {}
        return
        
    sorted_hits = sorted(glossary_hits, key=lambda x: len(x.get("english", "")), reverse=True)
    
    placeholders = {}
    masked_text = text
    
    for idx, hit in enumerate(sorted_hits):
        eng = hit.get("english", "").strip()
        jp = hit.get("japanese", "").strip()
        if not eng or not jp:
            continue
        placeholder = f"__G{idx}__"
        placeholders[placeholder] = jp
        
        pattern = re.compile(re.escape(eng), re.IGNORECASE)
        masked_text = pattern.sub(placeholder, masked_text)
        
    chunk["masked_text"] = masked_text
    chunk["placeholders"] = placeholders
    # Override source_text for LLM so it reads the masked text
    chunk["original_source"] = chunk["source_text"]
    chunk["source_text"] = masked_text

def unmask_glossary(chunk):
    translated = chunk.get("translation", "")
    if not isinstance(translated, str):
        translated = str(translated)
        
    placeholders = chunk.get("placeholders", {})
    
    if isinstance(placeholders, dict):
        for placeholder, jp_val in placeholders.items():
            num = placeholder.strip("_G")
            pattern_str = rf"__\s*[gG]\s*{num}\s*__"
            val_str = str(jp_val) if jp_val is not None else ""
            translated = re.sub(pattern_str, val_str, translated)
            
    chunk["translation"] = translated
    # Restore original source_text
    if "original_source" in chunk:
        chunk["source_text"] = chunk["original_source"]
        del chunk["original_source"]

def parse_json_tolerant(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    if content.startswith("\ufeff"):
        content = content[1:]
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
    text = re.sub(r",\s*([}\]])", r"\1", text)
    text = text.strip()
    if text.endswith(','):
        text = text[:-1].strip()
    text = re.sub(r'\b(\d+\.?\d*)f\b', r'\1', text)
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
        
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
                    if content.startswith("\ufeff"):
                        content = content[1:]
                    reader = csv.reader(io.StringIO(content))
                    header = next(reader, None)
                    if not header:
                        continue
                        
                    rows = list(reader)
                    
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
                    
                    def extract_flat_bracket(obj, current_path=""):
                        if isinstance(obj, dict):
                            for k, v in obj.items():
                                new_p = f"{current_path}['{k}']" if current_path else f"['{k}']"
                                extract_flat_bracket(v, new_p)
                        elif isinstance(obj, list):
                            for idx, v in enumerate(obj):
                                new_p = f"{current_path}[{idx}]"
                                extract_flat_bracket(v, new_p)
                        elif isinstance(obj, str):
                            cache[(rel_path, current_path, current_path)] = obj
                            
                    if ext == '.group':
                        fid = data.get('id', os.path.splitext(f)[0])
                        for key in ["displayName", "displayNameWithArticle", "displayNameLong", 
                                    "displayNameLongWithArticle", "displayNameIsOrAre", 
                                    "personNamePrefix", "personNamePrefixAOrAn"]:
                            if key in data and isinstance(data[key], str):
                                cache[(rel_path, f"{fid}.{key}", key) ] = data[key]
                        ranks = data.get("ranks", {})
                        if isinstance(ranks, dict):
                            for sec in ["ranks", "posts"]:
                                section = ranks.get(sec, {})
                                if isinstance(section, dict):
                                    for role, role_data in section.items():
                                        if isinstance(role_data, dict) and "name" in role_data:
                                            jp = f"ranks.{sec}.{role}.name"
                                            cache[(rel_path, f"{fid}.{jp}", jp)] = role_data["name"]
                        fleet = data.get("fleetTypeNames", {})
                        if isinstance(fleet, dict):
                            for fk, fv in fleet.items():
                                if isinstance(fv, str):
                                    jp = f"fleetTypeNames.{fk}"
                                    cache[(rel_path, f"{fid}.{jp}", jp)] = fv
                    else:
                        extract_flat_bracket(data)
                        
            except Exception as e:
                print(f"  [WARNING] Failed to load translations from {rel_path}: {e}")
                
    return cache

def main():
    print("Phase 3/4 - Agentic Translation Runner (Gemini Batched)")
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
    
    cached_count = 0
    skipped_proper_nouns = 0
    
    var_re = re.compile(r'^\$[a-zA-Z_]\w*$')
    opt_var_re = re.compile(r'^(\d+:)?[a-zA-Z_]\w*:\$[a-zA-Z_]\w*$')
    
    # Pre-process chunks: cache checking, skipping, and glossary masking
    for chunk in chunks:
        src_file = chunk["source_file"]
        row_key = chunk["row_key"]
        col = chunk["column"]
        source_text = chunk["source_text"]
        
        cache_key = (src_file, row_key, col)
        translation = trans_cache.get(cache_key)
        
        if not translation and src_file.endswith('.group'):
            short_key = row_key.split('.', 1)[-1] if '.' in row_key else row_key
            translation = trans_cache.get((src_file, short_key, col))
            
        if translation and translation.strip() and translation != source_text:
            chunk["translation"] = translation
            cached_count += 1
        else:
            context = chunk.get("context_tag", "")
            s_clean = source_text.strip()
            
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
                # Mask glossary terms for LLM
                mask_glossary(chunk)
                
    # Run batch translation
    print("Starting batch translation with Gemini...")
    from llm_client import batch_translate_sync, QuotaExhaustedError
    
    batch_size = 20
    translated_count = 0
    quota_exhausted = False
    
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        print(f"  Processing batch {i//batch_size + 1}/{(len(chunks) + batch_size - 1)//batch_size}...")
        
        try:
            batch = batch_translate_sync(batch)
        except QuotaExhaustedError as e:
            print(f"\n[FATAL] {e}")
            print("Daily API limit reached or extreme rate limiting applied.")
            print("Saving progress up to this point and gracefully exiting...")
            quota_exhausted = True
            break
            
        # Post-process this batch immediately
        for chunk in batch:
            if "placeholders" in chunk:
                unmask_glossary(chunk)
                
                source_text = chunk["source_text"]
                translated = chunk["translation"]
                
                source_placeholders = set(PLACEHOLDER_RE.findall(source_text))
                translated_placeholders = set(PLACEHOLDER_RE.findall(translated))
                
                missing_placeholders = source_placeholders - translated_placeholders
                if missing_placeholders:
                    print(f"  [CRITIC WARNING] Placeholders missing in translation of '{source_text[:20]}': {missing_placeholders}")
                    for placeholder in missing_placeholders:
                        translated += f" {placeholder}"
                        
                chunk["translation"] = translated
                translated_count += 1
                
        # Save incremental progress for all chunks processed so far
        with open(APPROVED_PATH, "w", encoding="utf-8", newline="") as f:
            json.dump(chunks, f, ensure_ascii=False, indent=2)
            
    print("\n" + "=" * 70)
    print("Translation and Critic Summary")
    print("=" * 70)
    print(f"Total chunks processed: {len(chunks)}")
    print(f"  Loaded from cache:   {cached_count}")
    print(f"  Skipped proper names: {skipped_proper_nouns}")
    print(f"  Newly translated:     {translated_count}")
    print(f"Wrote approved chunks to: {APPROVED_PATH}")
    print("=" * 70)
    
    if quota_exhausted:
        sys.exit(0)

if __name__ == "__main__":
    main()
