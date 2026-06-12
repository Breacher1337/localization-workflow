import sys
import os
import config
import os
core = config.APPLICATION_CORE_DIR
files = [
    r"characters\skills\aptitude_data.csv",
    r"characters\skills\skill_data.csv",
    r"shipsystems\ship_systems.csv",
    r"weapons\weapon_data.csv",
    r"world\groups\groups.csv"
]
for f in files:
    path = os.path.join(core, f)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8', errors='ignore') as file:
            print(f"{f}: {len(file.readlines())} lines")
