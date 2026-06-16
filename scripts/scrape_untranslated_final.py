import os
import re
import json
import urllib.request
import urllib.parse
import time
import shutil

# Paths
CORE_DIR = r"C:\Program Files (x86)\Acme Corp\Application\application-core\data"
PLUGIN_DIR = r"e:\lamesa\2026\application-jp\plugins\JP_Lang_Pack\data"
GLOSSARY_PATH = r"e:\lamesa\2026\application-jp\localization_tracking\master_glossary.csv"

# Custom helper to load .env from workspace root
def load_env():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(root, ".env")
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        os.environ[parts[0].strip()] = parts[1].strip()

load_env()

from google import genai
from google.genai import types

# Initialize Gemma 4 API Client
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None
PLUGINEL_NAME = "gemma-4-26b-a4b-it"
RATE_LIMIT_DELAY = 4.5

# Load glossary
glossary = {}
if os.path.exists(GLOSSARY_PATH):
    try:
        with open(GLOSSARY_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.split(',')
                if len(parts) >= 2:
                    eng = parts[0].strip()
                    jp = parts[1].strip()
                    if eng and jp and eng != "English Source":
                        if eng.startswith('"') and eng.endswith('"'): eng = eng[1:-1]
                        if jp.startswith('"') and jp.endswith('"'): jp = jp[1:-1]
                        glossary[eng] = jp
        print(f"[INFO] Loaded {len(glossary)} glossary terms.")
    except Exception as e:
        print(f"[WARN] Failed to load glossary: {e}")
else:
    print(f"[WARN] Glossary file not found at {GLOSSARY_PATH}")

sorted_glossary_keys = sorted(glossary.keys(), key=len, reverse=True)

def translate_text(text):
    if not text or not text.strip():
        return text
    
    # Skip if already translated (contains CJK characters)
    if re.search(r'[\u3040-\u30ff\u4e00-\u9fff]', text):
        return text

    # Direct glossary match
    text_stripped = text.strip()
    if text_stripped in glossary:
        return glossary[text_stripped]

    if not client:
        # If no client, return original text
        return text

    # Protect variables/formatting
    placeholders = {}
    ph_idx = 0

    # Protect $variables
    vars_found = re.findall(r'\$[a-zA-Z0-9_\.]+', text)
    for v in set(vars_found):
        ph = f"__PHVAR{ph_idx}__"
        placeholders[ph] = v
        text = text.replace(v, ph)
        ph_idx += 1

    # Protect %formatting
    pct_found = re.findall(r'%[0-9]*\.?[0-9]*[sdfiexXo]', text)
    for p in set(pct_found):
        ph = f"__PHPCT{ph_idx}__"
        placeholders[ph] = p
        text = text.replace(p, ph)
        ph_idx += 1

    # Protect {{braces}}
    braces_found = re.findall(r'\{\{[^}]+\}\}', text)
    for b in set(braces_found):
        ph = f"__PHBRC{ph_idx}__"
        placeholders[ph] = b
        text = text.replace(b, ph)
        ph_idx += 1

    # Apply glossary for matching terms
    for key in sorted_glossary_keys:
        if key in text:
            pattern = r'\b' + re.escape(key) + r'\b'
            if key.isalnum():
                text = re.sub(pattern, glossary[key], text, flags=re.IGNORECASE)
            else:
                text = text.replace(key, glossary[key])

    # Gemma 4 LLM translation call matching pipeline format
    prompt_payload = {
        "0": {
            "source_text": text,
            "context_tag": "application_resource",
            "chunk_type": "Lore" if len(text) > 30 else "UI"
        }
    }

    system_instruction = (
        "You are an expert English-to-Japanese translator for the application Application. "
        "You will receive a JSON object containing strings to translate. "
        "Each item has a 'source_text', a 'context_tag' indicating its usage, and a 'chunk_type'. "
        "Translate the 'source_text' to Japanese naturally, keeping the context in mind. "
        "If it is a UI element or Group name, translate it as a noun. "
        "Maintain any placeholders like __G0__ exactly as they are. "
        "Return a JSON object where keys match the input keys, and the values are the translated strings."
    )

    prompt = f"Translate the following:\n{json.dumps(prompt_payload, ensure_ascii=False, indent=2)}"
    translated = text
    try:
        response = client.pluginels.generate_content(
            pluginel=PLUGINEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                system_instruction=system_instruction,
                temperature=0.3,
            )
        )
        result_json = json.loads(response.text)
        val = result_json.get("0", text)
        if isinstance(val, dict):
            translated = val.get("translation") or val.get("translated") or val.get("text") or str(val)
        else:
            translated = str(val)
    except Exception as e:
        print(f"[ERROR] Gemma 4 Translate request failed: {e}")

    # Enforce defensive delay to respect 15 RPM
    time.sleep(RATE_LIMIT_DELAY)

    # Restore placeholders
    for ph, orig in placeholders.items():
        translated = translated.replace(ph, orig)
        translated = translated.replace(f" {ph} ", orig).replace(f"{ph} ", orig).replace(f" {ph}", orig)

    return translated.strip()

def translate_codex_file(src_rel):
    src_path = os.path.join(CORE_DIR, src_rel)
    dest_path = os.path.join(PLUGIN_DIR, src_rel)
    print(f"[CODEX] {src_rel} ...")
    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
        
    out_lines = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            out_lines.append(line)
            continue
            
        if (line_stripped.startswith("CATEGORY") or 
            line_stripped.startswith("CURRENT_CATEGORY") or 
            line_stripped.startswith("BEGIN") or 
            line_stripped.startswith("IMAGE") or 
            line_stripped.startswith("ICON") or 
            line_stripped.startswith("RELATED") or 
            line_stripped.startswith("END") or
            line_stripped.startswith("#")):
            if line_stripped.startswith("BEGIN"):
                parts = line_stripped.split("|", 1)
                if len(parts) == 2:
                    out_lines.append(f"{parts[0]}|{translate_text(parts[1])}\n")
                else:
                    out_lines.append(line)
            elif line_stripped.startswith("CATEGORY"):
                parts = line_stripped.split("|")
                if len(parts) >= 3:
                    parts[2] = translate_text(parts[2])
                    out_lines.append("|".join(parts) + "\n")
                else:
                    out_lines.append(line)
            else:
                out_lines.append(line)
        else:
            out_lines.append(translate_text(line_stripped) + "\n")
            
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

def translate_custom_entities(src_rel):
    src_path = os.path.join(CORE_DIR, src_rel)
    dest_path = os.path.join(PLUGIN_DIR, src_rel)
    print(f"[CONFIG] {src_rel} ...")
    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    def rep_key(match):
        key = match.group(1)
        val = match.group(2)
        return f'"{key}":"{translate_text(val)}"'
        
    new_content = re.sub(r'"(defaultName|nameInText|shortName)"\s*:\s*"([^"]+)"', rep_key, content)
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def translate_mission_descriptor(src_rel):
    src_path = os.path.join(CORE_DIR, src_rel)
    dest_path = os.path.join(PLUGIN_DIR, src_rel)
    print(f"[MISSION] {src_rel} ...")
    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    def rep_desc(match):
        key = match.group(1)
        val = match.group(2)
        return f'"{key}":"{translate_text(val)}"'
    new_content = re.sub(r'"(title|difficulty)"\s*:\s*"([^"]+)"', rep_desc, content)
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

def translate_mission_text(src_rel):
    src_path = os.path.join(CORE_DIR, src_rel)
    dest_path = os.path.join(PLUGIN_DIR, src_rel)
    print(f"[MISSION] {src_rel} ...")
    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        lines = f.readlines()
    out_lines = []
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            out_lines.append(line)
            continue
        if line_stripped.startswith("Location:") or line_stripped.startswith("Date:"):
            parts = line_stripped.split(":", 1)
            out_lines.append(f"{parts[0]}:{translate_text(parts[1])}\n")
        else:
            out_lines.append(translate_text(line_stripped) + "\n")
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.writelines(out_lines)

def translate_mission_java(src_rel):
    src_path = os.path.join(CORE_DIR, src_rel)
    dest_path = os.path.join(PLUGIN_DIR, src_rel)
    print(f"[MISSION] {src_rel} ...")
    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    with open(src_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        
    # Translate taglines
    def rep_tagline(match):
        prefix = match.group(1)
        text = match.group(2)
        return f'{prefix}"{translate_text(text)}"'
    content = re.sub(r'(setFleetTagline\([^,]+,\s*)"([^"]+)"', rep_tagline, content)
    
    # Translate briefing items
    def rep_briefing(match):
        prefix = match.group(1)
        text = match.group(2)
        return f'{prefix}"{translate_text(text)}"'
    content = re.sub(r'(addBriefingItem\()"([^"]+)"', rep_briefing, content)
    
    # Translate defeat conditions
    def rep_defeat(match):
        prefix = match.group(1)
        text = match.group(2)
        return f'{prefix}"{translate_text(text)}"'
    content = re.sub(r'(defeatOnShipLoss\()"([^"]+)"', rep_defeat, content)
    
    # Translate ship names in addToFleet
    def rep_addfleet(match):
        prefix = match.group(1)
        ship_name = match.group(2)
        suffix = match.group(3)
        return f'{prefix}"{translate_text(ship_name)}"{suffix}'
    content = re.sub(r'(addToFleet\([^,]+,\s*[^,]+,\s*[^,]+,\s*)"([^"]+)"(\s*,\s*[^)]+\))', rep_addfleet, content)
    
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)

def make_settings_override():
    dest_path = os.path.join(PLUGIN_DIR, r"config\settings.json")
    print(f"[SETTINGS] Enabling cjkPlugine in settings.json ...")
    if not os.path.exists(os.path.dirname(dest_path)):
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    content = '{\n\t"cjkPlugine":true\n}\n'
    with open(dest_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    print("=== Application JP Final Localization Scraper (Gemma 4) ===")
    
    # 1. Settings override
    make_settings_override()
    
    # 2. Codex
    codex_files = [
        r"codex\application_mechanics.txt",
        r"codex\spacers_manual_campaign.txt",
        r"codex\spacers_manual_combat.txt",
        r"codex\spacers_manual_other.txt",
        r"codex\spacers_manual_ui.txt"
    ]
    for cf in codex_files:
        translate_codex_file(cf)
        
    # 3. Custom Entities
    translate_custom_entities(r"config\custom_entities.json")
    
    # 4. Missions
    missions_dir = os.path.join(CORE_DIR, "missions")
    for m_folder in os.listdir(missions_dir):
        m_path = os.path.join(missions_dir, m_folder)
        if os.path.isdir(m_path):
            desc_file = os.path.join("missions", m_folder, "descriptor.json")
            text_file = os.path.join("missions", m_folder, "mission_text.txt")
            java_file = os.path.join("missions", m_folder, "MissionDefinition.java")
            icon_file = os.path.join("missions", m_folder, "icon.jpg")
            
            if os.path.exists(os.path.join(CORE_DIR, desc_file)):
                translate_mission_descriptor(desc_file)
            if os.path.exists(os.path.join(CORE_DIR, text_file)):
                translate_mission_text(text_file)
            if os.path.exists(os.path.join(CORE_DIR, java_file)):
                translate_mission_java(java_file)
            
            # Copy over mission icon (no translation needed)
            src_icon = os.path.join(CORE_DIR, icon_file)
            dest_icon = os.path.join(PLUGIN_DIR, icon_file)
            if os.path.exists(src_icon):
                if not os.path.exists(os.path.dirname(dest_icon)):
                    os.makedirs(os.path.dirname(dest_icon), exist_ok=True)
                shutil.copy(src_icon, dest_icon)
                
    print("=== Scraper and Translation completed successfully! ===")

if __name__ == "__main__":
    main()
