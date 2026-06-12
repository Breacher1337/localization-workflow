import sys
import os
import config
import csv
import sys

p_core = config.APPLICATION_CORE_DIR
p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

# STRICT newline='' to prevent Python from touching any \r\n
with open(p_core, 'r', encoding='cp1252', newline='') as f:
    core = list(csv.reader(f))

with open(p_plugin, 'r', encoding='utf-8', newline='') as f:
    plugin = list(csv.reader(f))

# Ensure they have the same length
assert len(core) == len(plugin), f"Row count mismatch! Core: {len(core)}, Plugin: {len(plugin)}"

# Copy columns 0, 1, 2, 3 EXACTLY
for i in range(len(core)):
    # Safely pad if somehow plugin is missing columns
    while len(plugin[i]) < 4:
        plugin[i].append("")
    while len(core[i]) < 4:
        core[i].append("")
        
    plugin[i][0] = core[i][0]
    plugin[i][1] = core[i][1]
    plugin[i][2] = core[i][2]
    plugin[i][3] = core[i][3]

# Write back strictly preserving \r\n using lineterminator='\r\n'
with open(p_plugin, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator='\r\n')
    writer.writerows(plugin)

print("SUCCESS: Copied columns 0-3 with strict newline preservation.")
