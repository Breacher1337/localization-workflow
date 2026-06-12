"""
Phase 0 Step B2: Glossary Auditor (7 checks)
Reads the unified glossary and performs structural validation.
"""
import csv
import os
import re
import sys
import io
import json

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOSSARY = r".\localization_tracking\master_glossary.csv"
PLUGIN_DIR = r".\plugins\JP_Lang_Pack\data"
SANITIZER = r".\sanitize_groups.py"
REPORT_FILE = r".\localization_tracking\glossary_audit_report.txt"

# --- Load glossary ---
glossary = []
with open(GLOSSARY, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        if row:
            glossary.append(row)

print(f"Loaded {len(glossary)} glossary entries.")
print(f"Header: {header}")
print()

warnings = []
errors = []

# === CHECK 1: FORMAT — Does every row have all 5 columns? ===
print("=== CHECK 1: FORMAT ===")
for i, row in enumerate(glossary):
    if len(row) < 5:
        errors.append(f"Row {i+2}: Only {len(row)} columns (need 5): {row[0] if row else '(empty)'}")
    elif any(cell.strip() == "" for cell in row[:3]):
        warnings.append(f"Row {i+2}: Empty required field in first 3 columns: {row}")
issues_1 = len([e for e in errors if "columns" in e])
print(f"  {issues_1} format errors found.")

# === CHECK 2: TYPE COVERAGE — Does every entry have a valid Type? ===
print("=== CHECK 2: TYPE COVERAGE ===")
valid_types = {"Group", "Map/Planet", "Map/System", "Rank/Post", "Item", "UI/Combat",
               "UI/Lore", "Character", "Lore", "Location", "Ability", "Industry",
               "Market Condition", "Name", "Ship Class", "Applicationplay", "Ship/Lore", "Title"}
for i, row in enumerate(glossary):
    if len(row) >= 3:
        t = row[2].strip()
        if t and t not in valid_types:
            warnings.append(f"Row {i+2}: Unknown type '{t}' for '{row[0]}'")
        elif not t:
            warnings.append(f"Row {i+2}: Missing type for '{row[0]}'")
type_issues = len([w for w in warnings if "type" in w.lower() or "Unknown type" in w])
print(f"  {type_issues} type issues found.")

# === CHECK 3: COLLISION — Two English terms → same Japanese? ===
print("=== CHECK 3: COLLISION DETECTION ===")
jp_to_en = {}
for row in glossary:
    if len(row) >= 2:
        jp = row[1].strip()
        en = row[0].strip()
        if jp in jp_to_en and jp_to_en[jp] != en:
            warnings.append(f"Collision: '{jp_to_en[jp]}' and '{en}' both map to '{jp}'")
        jp_to_en[jp] = en
collisions = len([w for w in warnings if "Collision" in w])
print(f"  {collisions} collisions found.")

# === CHECK 4: SANITIZER SYNC — Does sanitizer match glossary? ===
print("=== CHECK 4: SANITIZER SYNC ===")
if os.path.exists(SANITIZER):
    with open(SANITIZER, "r", encoding="utf-8") as f:
        sanitizer_code = f.read()
    # Extract replacement dict
    match = re.search(r'replacements\s*=\s*\{([^}]+)\}', sanitizer_code, re.DOTALL)
    if match:
        # Parse simple key-value pairs
        pairs = re.findall(r'r?"([^"]+)":\s*"([^"]+)"', match.group(1))
        glossary_jp = {row[1].strip() for row in glossary if len(row) >= 2}
        for pattern, replacement in pairs:
            if replacement not in glossary_jp:
                errors.append(f"Sanitizer target '{replacement}' (from pattern '{pattern}') not found in glossary")
            else:
                pass
    sync_issues = len([e for e in errors if "Sanitizer" in e])
    print(f"  {sync_issues} sync issues found.")
else:
    print("  Sanitizer file not found, skipping.")

# === CHECK 5: EXISTENCE — Scan plugin files for glossary English terms ===
print("=== CHECK 5: EXISTENCE (scanning plugin files) ===")
# We check if the *Japanese* translations actually appear in the plugin files
plugin_content = ""
file_count = 0
for root, _, files in os.walk(PLUGIN_DIR):
    for f in files:
        if f.endswith(('.csv', '.json', '.group')):
            try:
                with open(os.path.join(root, f), 'r', encoding='utf-8') as fh:
                    plugin_content += fh.read()
                file_count += 1
            except:
                pass
print(f"  Scanned {file_count} plugin files.")
unused = []
for row in glossary:
    if len(row) >= 2 and row[1].strip():
        jp = row[1].strip()
        if jp not in plugin_content and row[0].strip().lower() not in plugin_content.lower():
            unused.append(row[0].strip())
if unused:
    for u in unused:
        warnings.append(f"Not found in plugin files: '{u}'")
print(f"  {len(unused)} glossary terms not found in any plugin file.")

# === CHECK 6: DUPLICATE ENGLISH KEYS ===
print("=== CHECK 6: DUPLICATE KEYS ===")
en_seen = {}
for i, row in enumerate(glossary):
    if len(row) >= 1:
        key = row[0].strip().lower()
        if key in en_seen:
            errors.append(f"Duplicate English key '{row[0]}' at rows {en_seen[key]+2} and {i+2}")
        en_seen[key] = i
dup_count = len([e for e in errors if "Duplicate" in e])
print(f"  {dup_count} duplicates found.")

# === CHECK 7: PLUGIN FILE DRIFT — Japanese in plugin files that doesn't match glossary ===
print("=== CHECK 7: FACTION DRIFT SCAN ===")
# Check for known bad patterns that should have been sanitized
known_bad_patterns = [
    ("独立した", "Should be 独立勢力"),
    ("覇権", "Should be ヘゲモニー"),
    ("ルゥディック", "Should be ルッディック"),
    ("ルダイック", "Should be ルッディック"),
    ("ラディック", "Should be ルッディック"),
    ("トリタキオン", "Should be トライ・タキオン"),
    ("ペルシア同盟", "Should be ペルセアン同盟"),
]
drift_count = 0
for pattern, msg in known_bad_patterns:
    count = plugin_content.count(pattern)
    if count > 0:
        errors.append(f"DRIFT: Found {count} instances of '{pattern}' — {msg}")
        drift_count += count
print(f"  {drift_count} drift instances found.")

# === SUMMARY ===
print()
print("=" * 60)
print(f"AUDIT SUMMARY")
print(f"  Total glossary entries: {len(glossary)}")
print(f"  Errors:   {len(errors)}")
print(f"  Warnings: {len(warnings)}")
print("=" * 60)

if errors:
    print("\n--- ERRORS ---")
    for e in errors:
        print(f"  ❌ {e}")

if warnings:
    print(f"\n--- WARNINGS ({len(warnings)} total, showing first 20) ---")
    for w in warnings[:20]:
        print(f"  ⚠️ {w}")
    if len(warnings) > 20:
        print(f"  ... and {len(warnings)-20} more.")

# Write report
with open(REPORT_FILE, "w", encoding="utf-8") as f:
    f.write(f"Glossary Audit Report\n{'='*40}\n")
    f.write(f"Entries: {len(glossary)}\nErrors: {len(errors)}\nWarnings: {len(warnings)}\n\n")
    f.write("ERRORS:\n")
    for e in errors:
        f.write(f"  {e}\n")
    f.write("\nWARNINGS:\n")
    for w in warnings:
        f.write(f"  {w}\n")
print(f"\nReport written to: {REPORT_FILE}")
