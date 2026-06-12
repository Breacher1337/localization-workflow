import sys

path = r'.\compile.bat'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('set CLASSPATH="%APPLICATION_CORE%\\legacyapp.api.jar";"%APPLICATION_CORE%\\log4j-1.2.9.jar";"%LIBS_DIR%\\javassist.jar"',
                    'set CLASSPATH="%APPLICATION_CORE%\\legacyapp.api.jar";"%APPLICATION_CORE%\\log4j-1.2.9.jar";"%APPLICATION_CORE%\\json.jar";"%LIBS_DIR%\\javassist.jar"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
