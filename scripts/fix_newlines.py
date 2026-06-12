import os
plugin_dir = r'.\plugins\JP_Lang_Pack\data'
count = 0
for root, _, files in os.walk(plugin_dir):
    for f in files:
        if f.endswith('.csv'):
            path = os.path.join(root, f)
            try:
                with open(path, 'rb') as file:
                    data = file.read()
                
                # Replace \r\n with \n first, then replace \n with \r\n
                new_data = data.replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')
                
                if new_data != data:
                    with open(path, 'wb') as file:
                        file.write(new_data)
                    count += 1
                    print('Fixed newlines in:', path)
            except Exception as e:
                print('Error processing', path, e)
print('Fixed newlines in', count, 'files.')
