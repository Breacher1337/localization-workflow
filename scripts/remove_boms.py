import os
plugin_dir = r'.\plugins\JP_Lang_Pack'
count = 0
for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.json') or f.endswith('.csv'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as file:
                    data = file.read()
                if data.startswith(b'\xef\xbb\xbf'):
                    data = data[3:]
                    with open(path, 'wb') as file:
                        file.write(data)
                    count += 1
            except Exception as e:
                print('Error processing', path, e)
print('Removed BOM from', count, 'files.')
