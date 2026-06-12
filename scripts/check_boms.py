import os
import glob
plugin_dir = r'.\plugins\JP_Lang_Pack'
for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.json') or f.endswith('.csv'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as file:
                    if file.read(3) == b'\xef\xbb\xbf':
                        print('Found BOM in:', path)
            except Exception:
                pass
print('Done checking BOMs.')
