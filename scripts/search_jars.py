import sys
import os
import config
﻿import zipfile

jars = [
    config.APPLICATION_CORE_DIR,
    config.APPLICATION_CORE_DIR,
    config.APPLICATION_CORE_DIR
]

query = b"Open a comm link"

for jar in jars:
    try:
        with zipfile.ZipFile(jar, 'r') as z:
            for info in z.infolist():
                with z.open(info) as f:
                    content = f.read()
                    if query in content:
                        print(f"Found in {jar}: {info.filename}")
    except Exception as e:
        print(f"Error reading {jar}: {e}")
