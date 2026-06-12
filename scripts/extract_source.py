import sys
import os
import config
import zipfile

zip_path = config.APPLICATION_CORE_DIR
out_dir = r".\source"

with zipfile.ZipFile(zip_path, 'r') as z:
    for filename in z.namelist():
        if "PirateSystemBounty.java" in filename or "CoreRuleTokenReplacementGeneratorImpl.java" in filename:
            z.extract(filename, out_dir)
            print(f"Extracted {filename}")
