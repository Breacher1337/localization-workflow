"""
Phase 9: Apply Critic-identified fixes to JSON files.
Covers: tips.json, tooltips.json, ship_names.json, default_ranks.json
"""
import json
import os
import sys
import io
import re

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PLUGIN = r".\plugins\JP_Lang_Pack\data"

def fix_file(filepath, replacements, description):
    """Apply a list of (old, new) replacements to a file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    count = 0
    for old, new in replacements:
        if old in content:
            n = content.count(old)
            content = content.replace(old, new)
            count += n
            print(f"  ✅ {old} → {new} ({n}x)")
    
    if count > 0:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
        print(f"  Total: {count} replacements in {os.path.basename(filepath)}")
    else:
        print(f"  No replacements needed in {os.path.basename(filepath)}")
    return count

# === tips.json ===
print("=== FIXING tips.json ===")
tips_fixes = [
    # HIGH: 磁束 → フラックス (systematic)
    ("磁束", "フラックス"),
    # HIGH: 光束 → フラックス (line 9)
    ("光束", "フラックス"),
    # HIGH: 盾 → シールド (line 15, in context of "運動ダメージは盾に対して")
    ("運動ダメージは盾に対して", "運動ダメージはシールドに対して"),
    # HIGH: 鎧 → 装甲 (line 15)
    ("爆発によるダメージは鎧に対して", "爆発によるダメージは装甲に対して"),
    # HIGH: 改造車 → 改造 (typo, line 58)
    ("船体改造車", "船体改造"),
    # MEDIUM: 艦艇 → 艦船 (consistent term)
    ("艦艇", "艦船"),
    # MEDIUM: 船舶 → 艦船 (consistent term)
    ("船舶", "艦船"),
    # MEDIUM: ダメージ タイプ → ダメージタイプ (remove space, line 17)
    ("ダメージ タイプ", "ダメージタイプ"),
    # MEDIUM: ハードポイント スロット → ハードポイントスロット (remove space, line 49)
    ("ハードポイント スロット", "ハードポイントスロット"),
    # MEDIUM: フリゲート艦 → フリゲート (redundant suffix, line 57)
    ("フリゲート艦", "フリゲート"),
    # MEDIUM: 戦闘準備状態 → 戦闘準備態勢 (consistency with strings.json)
    ("戦闘準備状態", "戦闘準備態勢"),
    # MEDIUM: ストーリー ポイント → ストーリーポイント (remove space, line 58)
    ("ストーリー ポイント", "ストーリーポイント"),
    # MEDIUM: ドメイン サイクル → ドメインサイクル (remove space, line 56)
    ("ドメイン サイクル", "ドメインサイクル"),
    # MEDIUM: エネルギー武器 → エネルギー兵器 (consistency, line 17)
    ("エネルギー武器", "エネルギー兵器"),
    # MEDIUM: 武器選択メニュー → 兵器選択メニュー (line 21)
    ("武器選択メニュー", "兵器選択メニュー"),
    # MEDIUM: 散逸 → 消散 (consistency, line 37)
    ("散逸", "消散"),
]
fix_file(os.path.join(PLUGIN, "strings", "tips.json"), tips_fixes, "tips.json")

# === tooltips.json ===
print("\n=== FIXING tooltips.json ===")
tooltips_fixes = [
    ("戦闘準備状態", "戦闘準備態勢"),
]
fix_file(os.path.join(PLUGIN, "strings", "tooltips.json"), tooltips_fixes, "tooltips.json")

# === ship_names.json ===
print("\n=== FIXING ship_names.json ===")
ship_fixes = [
    ("チコモストク", "チコモズトック"),
]
fix_file(os.path.join(PLUGIN, "strings", "ship_names.json"), ship_fixes, "ship_names.json")

# === default_ranks.json ===
print("\n=== FIXING default_ranks.json ===")
ranks_fixes = [
    ('"家長世代"', '"氏族女家長"'),
]
fix_file(os.path.join(PLUGIN, "world", "groups", "default_ranks.json"), ranks_fixes, "default_ranks.json")

print("\n=== ALL JSON FIXES COMPLETE ===")
