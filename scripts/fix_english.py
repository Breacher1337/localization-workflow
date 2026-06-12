import csv, re

path = r'.\plugins\JP_Lang_Pack\data\campaign\rules.csv'

with open(path, 'r', encoding='utf-8') as f:
    rows = list(csv.reader(f))

header = rows[0]
text_idx = header.index('text')

replacements = {
    # Specifically requested
    r'(?i)\btriiPad\b': 'Tripad',
    r'(?i)\btripiPad\b': 'Tripad',
    r'(?i)\btripad\b': 'トライパッド', # Actually let's use Katakana to completely localize it properly
    r'\bTripad\b': 'トライパッド',
    r'\bTriPad\b': 'トライパッド',
    r'\btripad\b': 'トライパッド',
    r'\bTriiPad\b': 'トライパッド',
    r'\bTripiPad\b': 'トライパッド',
    r'(?i)\s*corporation\b': '社',
    r'(?i)\bping\b': '通知',
    
    # Missing names
    r'\bKeepfaith\b': 'キープフェイス',
    r'\bCoureuse\b': 'クールーズ',
    r'\bFabrique\b': 'ファブリク',
    r'\bOrbitale\b': 'オービタール',
    r'\bSkiron\b': 'スキロン',
    r'\bSebestyen\b': 'セベスチェン',
    r'\bGargoyle\b': 'ガーゴイル',
    r'\bPathers\b': 'パス教徒',
    r'\bPather\b': 'パス教徒',
    r'\bMenes\b': 'メネス',
    r'\bGlamour\b': 'グラマー',
    r'\bSubcurate\b': '副司祭',
    r'\bAcademy\b': 'アカデミー',
    r'\bRotanev\b': 'ロタネフ',
    r'\bBornanew\b': 'ボルナニュー',
    r'\bZal\b': 'ザル',
    r'\bJanus\b': 'ヤヌス',
    r'\bExcubitor\b': 'エクスキュービター',
    r'\bOrbis\b': 'オービス',
    r'\bComms\b': '通信',
    r'\bArtemisia\b': 'アルテミシア',
    r'\bYaribay\b': 'ヤリベイ',
    r'\bDaud\b': 'ダウド',
    r'\bDiktat\b': 'ディクテート',
    r'\bHegemony\b': 'ヘゲモニー',
    r'\bSkyarco\b': 'スカイアルコ',
    r'\bElissa\b': 'エリッサ',
    r'\bJethro\b': 'ジェスロ',
    r'\bKallichore\b': 'カリコレ',
    r'\bRotanev\b': 'ロタネフ',
    r'\bsad smile\b': '悲しい笑顔',
    r'\bsays\b': 'と言う',
}

for row in rows[1:]:
    text = row[text_idx]
    if not text: continue
    
    # apply regexes
    for pattern, repl in replacements.items():
        text = re.sub(pattern, repl, text)
        
    row[text_idx] = text

with open(path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(rows)

print("Applied English replacements successfully!")
