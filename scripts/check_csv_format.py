import sys
import os
import config
import csv
import sys

p_core = config.APPLICATION_CORE_DIR
p_plugin = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

with open(p_core, 'rb') as f:
    core_raw = f.read()

with open(p_plugin, 'rb') as f:
    plugin_raw = f.read()

print('Core has double quotes (""):', b'""' in core_raw)
print('Plugin has double quotes (""):', b'""' in plugin_raw)
print('Core has escaped quotes (\\"):', b'\\"' in core_raw)
print('Plugin has escaped quotes (\\"):', b'\\"' in plugin_raw)

print('Plugin has \\r\\r\\n:', b'\r\r\n' in plugin_raw)
print('Core has \\r\\r\\n:', b'\r\r\n' in core_raw)
