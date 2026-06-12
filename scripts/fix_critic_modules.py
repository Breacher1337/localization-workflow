"""
Phase 9: Apply Critic-identified fixes to group files.
All replacements are surgical — only the specific strings are changed.
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

FACTION_DIR = r".\plugins\JP_Lang_Pack\data\world\groups"

# Define all fixes: (filename, old_string, new_string, severity, description)
fixes = [
    # === HIGH PRIORITY ===
    ("tritachyon.group",
     '"Director of Special Acquisitions"',
     '"特別調達ディレクター"',
     "HIGH", "Untranslated English text"),

    ("sindrian_diktat.group",
     '"シンドリアのディクタット"',
     '"シンドリアン・ディクタット"',
     "HIGH", "displayNameWithArticle mismatches displayName"),

    ("sindrian_diktat.group",
     '"コントローラー全般"',
     '"総監"',
     "HIGH", "Controller-General: glossary says 総監"),

    ("persean_league.group",
     '"家長世代"',
     '"氏族女家長"',
     "HIGH", "Gens Matriarch: glossary says 氏族女家長"),

    ("luddic_path.group",
     '"ルッディックな道"',
     '"ルッディック・パス"',
     "HIGH", "displayNameWithArticle: should match displayName"),

    # === MEDIUM PRIORITY ===
    ("tritachyon.group",
     '"トライウェイ スペースライン フライト"',
     '"トライウェイ・スペースライン・フライト"',
     "MEDIUM", "Use nakaguro instead of space separators"),

    ("sindrian_diktat.group",
     '"社内警備部隊"',
     '"内部警備部隊"',
     "MEDIUM", "社内 implies corporation; Diktat is a state"),

    ("pirates.group",
     '"旅客車列"',
     '"旅客船団"',
     "MEDIUM", "車列 is land vehicles; 船団 is fleet/convoy"),

    ("independent.group",
     '"独立派"',
     '"独立勢力"',
     "MEDIUM", "Unify to glossary term 独立勢力"),

    ("independent.group",
     '"独立系"',
     '"独立勢力"',
     "MEDIUM", "Unify to glossary term 独立勢力"),

    # Navarch consistency: ナバーチ → ナヴァーチ (match glossary's Navarch)
    ("persean_league.group",
     '"デミ・ナバーチ"',
     '"デミ・ナヴァーチ"',
     "MEDIUM", "Consistent with ナヴァーチ (Navarch)"),
]

total_applied = 0
for filename, old, new, severity, desc in fixes:
    filepath = os.path.join(FACTION_DIR, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if old in content:
        content = content.replace(old, new)
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  ✅ [{severity}] {filename}: {desc}")
        print(f"     {old} → {new}")
        total_applied += 1
    else:
        print(f"  ⚠️ [{severity}] {filename}: Pattern not found: {old}")

print(f"\nApplied {total_applied} fixes across group files.")
