import sys
import os
import config
﻿import zipfile

with zipfile.ZipFile(config.APPLICATION_CORE_DIR, 'r') as z:
    for name in z.namelist():
        if 'SettingsAPI' in name:
            print(name)
