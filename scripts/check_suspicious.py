import os
plugin_dir = r'.\plugins\JP_Lang_Pack\data'
for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv') or f.endswith('.json'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as file:
                    data = file.read(10)
                first_byte = data[:1]
                if not first_byte.isalpha() and first_byte not in b'{"\'[':
                    print('Suspicious:', path.split('data\\')[-1], data)
            except Exception as e:
                print('Error processing', path, e)
