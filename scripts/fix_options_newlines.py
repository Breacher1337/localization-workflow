import sys
import os
import config
import csv
import re
import sys

p_core = config.APPLICATION_CORE_DIR
p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

with open(p_core, 'r', encoding='cp1252', newline='') as f:
    core = list(csv.reader(f))

with open(p_plugin, 'r', encoding='utf-8', newline='') as f:
    plugin = list(csv.reader(f))

assert len(core) == len(plugin), "Row count mismatch!"

fixed_count = 0

for i in range(len(core)):
    if len(core[i]) <= 5 or len(plugin[i]) <= 5:
        continue
        
    core_opt = core[i][5]
    plugin_opt = plugin[i][5]
    
    if not core_opt or not plugin_opt:
        continue
        
    # If the vanilla option has newlines
    if '\n' in core_opt:
        # Extract all option IDs from the vanilla text.
        # An option ID is at the start of a line, before a colon.
        lines = core_opt.replace('\r\n', '\n').split('\n')
        option_ids = []
        for line in lines:
            if ':' in line:
                opt_id = line.split(':', 1)[0].strip()
                if opt_id:
                    option_ids.append(opt_id)
        
        # Now, reconstruct the plugin_opt string by enforcing newlines before each option_id
        # We start from the second option ID, as the first one is at the start.
        if len(option_ids) > 1:
            new_plugin_opt = plugin_opt
            for opt_id in option_ids[1:]:
                search_str = opt_id + ':'
                # If the string exists and doesn't already have a newline before it
                idx = new_plugin_opt.find(search_str)
                if idx > 0 and new_plugin_opt[idx-1] != '\n':
                    # Insert \r\n before it
                    new_plugin_opt = new_plugin_opt[:idx] + '\r\n' + new_plugin_opt[idx:]
            
            if new_plugin_opt != plugin_opt:
                plugin[i][5] = new_plugin_opt
                fixed_count += 1

with open(p_plugin, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, lineterminator='\r\n')
    writer.writerows(plugin)

print(f"SUCCESS: Restored newlines in the options column for {fixed_count} rows.")
