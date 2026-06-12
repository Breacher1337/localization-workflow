"""
Phase 0 Step A+B1: Apply human-approved corrections and merge root-only entries.

Decisions made by human arbiter:
- Luddic → ルッディック (phonetic of "Luddic", not "Luddite"/ルッダイト)
- Tri-Tachyon → トライ・タキオン (WITH nakaguro)
- Sindrian Diktat → シンドリアン・ディクタット (with ン)
- Star system names → pure phonetic katakana
- Derelict → デレリクト (phonetic noun)
"""
import csv
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GLOSSARY = r".\localization_tracking\master_glossary.csv"

# === CORRECTIONS (key=English Source lowercase, value=new Japanese) ===
corrections = {
    "algebbar": "アルゲバール",
    "corvus": "コルヴス",
    "hybrasil": "ハイブラジル",
    "magec": "マゲク",
    "tyle": "タイル",
    "westernesse": "ウェスタネッセ",
    "neutral": "ニュートラル",
    "sleeper": "スリーパー",
    "derelict": "デレリクト",
    "controller-general": "総監",
    "gens matriarch": "氏族女家長",
    "diktat": "ディクタット",
    "tri-tachyon": "トライ・タキオン",
}

# === ROOT-ONLY ENTRIES TO ADD ===
root_entries = [
    ("Flux", "フラックス", "Applicationplay", "Energy capacity/shield stress", "Merged"),
    ("Ordnance Points", "兵器ポイント", "Applicationplay", "Points used to equip weapons and hullplugins", "Merged"),
    ("Hull", "船体", "Applicationplay", "The physical body of a ship", "Merged"),
    ("Armor", "装甲", "Applicationplay", "Defensive plating", "Merged"),
    ("CR (Combat Readiness)", "戦闘準備(CR)", "Applicationplay", "How ready a ship is for battle", "Merged"),
    ("Deployment Points", "配備ポイント", "Applicationplay", "Cost to deploy a ship in combat", "Merged"),
    ("Hyperspace", "超空間(ハイパースペース)", "Lore", "Faster-than-light travel dimension", "Merged"),
    ("Jump Point", "ジャンプポイント", "Lore", "Entry/exit points to hyperspace", "Merged"),
    ("Burn Level", "バーンレベル", "Applicationplay", "Speed of a fleet in campaign plugine", "Merged"),
    ("D-Plugin", "D-PLUGIN", "Applicationplay", "Degraded/damaged pluginification on a ship", "Merged"),
    ("S-Plugin", "S-PLUGIN", "Applicationplay", "Story pluginification built into a ship", "Merged"),
    ("PD (Point Defense)", "PD(近接防衛)", "Applicationplay", "Anti-missile and anti-fighter weapons", "Merged"),
    ("EMP", "EMP", "Applicationplay", "Electromagnetic pulse damage", "Merged"),
    ("Fighter", "戦闘機", "Ship Class", "Small craft deployed from carriers", "Merged"),
    ("Bomber", "爆撃機", "Ship Class", "Small craft focused on anti-ship payloads", "Merged"),
    ("Interceptor", "迎撃機", "Ship Class", "Small craft focused on anti-fighter roles", "Merged"),
    ("Carrier", "空母", "Ship Class", "Ship dedicated to deploying fighters", "Merged"),
    ("Frigate", "フリゲート", "Ship Class", "Smallest standard ship class", "Merged"),
    ("Destroyer", "駆逐艦", "Ship Class", "Medium-small ship class", "Merged"),
    ("Cruiser", "巡洋艦", "Ship Class", "Medium-large ship class", "Merged"),
    ("Capital", "主力艦", "Ship Class", "Largest ship class", "Merged"),
    ("Domain of Man", "人類領域(ドメイン)", "Lore", "The fallen human empire", "Merged"),
    ("Luddic Church", "ルッディック教会", "Group", "Religious group", "Merged"),
    ("AI Core", "AIコア", "Item", "Artificial intelligence unit (Alpha/Beta/Gamma)", "Merged"),
    ("Story Point", "ストーリーポイント", "Applicationplay", "Special currency for unique choices", "Merged"),
]

# Read current glossary
with open(GLOSSARY, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    rows = list(reader)

print(f"Read {len(rows)} entries from glossary.")

# Apply corrections
corrected = 0
for i, row in enumerate(rows):
    if not row:
        continue
    key = row[0].strip().lower()
    if key in corrections:
        old = row[1]
        row[1] = corrections[key]
        # Update status
        if len(row) >= 5:
            row[4] = "Human-Approved"
        print(f"  CORRECTED: {row[0]:30s} {old} → {row[1]}")
        corrected += 1

# Check which root entries already exist (case-insensitive)
existing_keys = {r[0].strip().lower() for r in rows if r}
added = 0
for entry in root_entries:
    if entry[0].strip().lower() not in existing_keys:
        rows.append(list(entry))
        print(f"  ADDED: {entry[0]:30s} → {entry[1]}")
        added += 1
    else:
        pass  # Already exists, skip

# Write back
with open(GLOSSARY, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for row in rows:
        if row:  # skip empty rows
            writer.writerow(row)

print(f"\nDone. Corrected {corrected}, added {added}. Total: {len([r for r in rows if r])} entries.")
