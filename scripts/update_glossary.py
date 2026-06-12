import csv

path = r'.\localization_tracking\master_glossary.csv'

new_entries = [
    ['Tripad', 'トライパッド', 'UI/Lore', 'Common personal datapad in Application', 'Manual Update'],
    ['ping', '通知', 'UI/Lore', 'Notification or transmission ping', 'Manual Update'],
    ['Corporation', '社', 'Lore', 'Corporate suffix', 'Manual Update'],
    ['corporation', '企業', 'Lore', 'Corporate noun', 'Manual Update'],
    ['Keepfaith', 'キープフェイス', 'Character', '', 'Manual Update'],
    ['Coureuse', 'クールーズ', 'Character', '', 'Manual Update'],
    ['Fabrique Orbitale', 'ファブリク・オービタール', 'Location', '', 'Manual Update'],
    ['Skiron', 'スキロン', 'Location', '', 'Manual Update'],
    ['Sebestyen', 'セベスチェン', 'Character', '', 'Manual Update'],
    ['Gargoyle', 'ガーゴイル', 'Character', '', 'Manual Update'],
    ['Pather', 'パス教徒', 'Group', '', 'Manual Update'],
    ['Menes', 'メネス', 'Character', '', 'Manual Update'],
    ['Glamour', 'グラマー', 'Character', '', 'Manual Update'],
    ['Subcurate', '副司祭', 'Title', '', 'Manual Update'],
    ['Academy', 'アカデミー', 'Location', 'Galatia Academy', 'Manual Update'],
    ['Rotanev', 'ロタネフ', 'Location', '', 'Manual Update'],
    ['Bornanew', 'ボルナニュー', 'Character', '', 'Manual Update'],
    ['Zal', 'ザル', 'Character', '', 'Manual Update'],
    ['Janus', 'ヤヌス', 'Lore', 'Janus Device', 'Manual Update'],
    ['Excubitor', 'エクスキュービター', 'Ship/Lore', '', 'Manual Update'],
    ['Orbis', 'オービス', 'Location', '', 'Manual Update'],
    ['Comms', '通信', 'UI/Lore', '', 'Manual Update'],
    ['Artemisia', 'アルテミシア', 'Character', '', 'Manual Update'],
    ['Yaribay', 'ヤリベイ', 'Character', '', 'Manual Update'],
    ['Daud', 'ダウド', 'Character', '', 'Manual Update'],
    ['Diktat', 'ディクテート', 'Group', 'Sindrian Diktat', 'Manual Update'],
    ['Hegemony', 'ヘゲモニー', 'Group', '', 'Manual Update'],
    ['Skyarco', 'スカイアルコ', 'Location', '', 'Manual Update'],
    ['Elissa', 'エリッサ', 'Character', '', 'Manual Update'],
    ['Jethro', 'ジェスロ', 'Character', '', 'Manual Update'],
    ['Kallichore', 'カリコレ', 'Lore', '', 'Manual Update']
]

with open(path, 'a', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(new_entries)

print(f'Successfully added {len(new_entries)} items to master_glossary.csv!')
