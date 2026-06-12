import sys
import os
import config
import os
import zipfile

core_dir = config.APPLICATION_CORE_DIR

def search_in_jar(jar_path, term):
    with zipfile.ZipFile(jar_path, 'r') as z:
        for filename in z.namelist():
            try:
                content = z.read(filename)
                if term.encode('utf-8') in content:
                    print(f"Found {term} in {jar_path} -> {filename}")
            except Exception as e:
                pass

for f in os.listdir(core_dir):
    if f.endswith('.jar'):
        print(f"Searching {f}...")
        search_in_jar(os.path.join(core_dir, f), 'psb_manOrWoman')
        search_in_jar(os.path.join(core_dir, f), 'shipOrFleet')
