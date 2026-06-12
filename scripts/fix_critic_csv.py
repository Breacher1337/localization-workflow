"""
Phase 9: Apply Critic-identified fixes to CSV files.
Covers: hull_plugins.csv, descriptions.csv
abilities.csv PASSED — no changes needed.
"""
import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PLUGIN = r".\plugins\JP_Lang_Pack\data"

def fix_file(filepath, replacements):
    """Apply replacements and report."""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    total = 0
    for old, new in replacements:
        if old in content:
            n = content.count(old)
            content = content.replace(old, new)
            total += n
            print(f"  ✅ {old} → {new} ({n}x)")
    
    if total > 0:
        with open(filepath, 'w', encoding='utf-8', newline='') as f:
            f.write(content)
    print(f"  Total: {total} replacements in {os.path.basename(filepath)}")
    return total

# === hull_plugins.csv ===
print("=== FIXING hull_plugins.csv ===")
hull_fixes = [
    # CRITICAL: 磁束 → フラックス (systematic, ~30+ instances)
    ("磁束", "フラックス"),
    # CRITICAL: 流束 → フラックス (safety overrides, line 86-90)
    ("流束", "フラックス"),
    # MEDIUM: 艦艇 → 艦船
    ("艦艇", "艦船"),
    # MEDIUM: 散逸 → 消散 (consistency)
    ("散逸", "消散"),
]
fix_file(os.path.join(PLUGIN, "hullplugins", "hull_plugins.csv"), hull_fixes)

# === descriptions.csv ===
print("\n=== FIXING descriptions.csv ===")
desc_fixes = [
    # CRITICAL: 磁束 → フラックス
    ("磁束", "フラックス"),
    # CRITICAL: 2000年高性能爆発物 → 2000高性能爆発 (damage value, NOT a year)
    ("2000年高性能爆発物", "2000高性能爆発"),
    # MEDIUM: 艦艇 → 艦船
    ("艦艇", "艦船"),
    # MEDIUM: 修理と修理 → 修理と改装 (Repair and Refit, not Repair and Repair)
    ("修理と修理", "修理と改装"),
    # MEDIUM: ハラスメント → 妨害攻撃 (combat order, not sexual harassment)
    ("ハラスメント", "妨害攻撃"),
]
fix_file(os.path.join(PLUGIN, "strings", "descriptions.csv"), desc_fixes)

print("\n=== ALL CSV FIXES COMPLETE ===")
