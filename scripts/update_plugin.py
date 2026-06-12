import sys

with open(r'.\source\com\applicationjp\JPTranslationPlugin.java', 'r', encoding='utf-8') as f:
    content = f.read()

new_translations = '''
        TR.put("Open a comm link", "通信リンクを開く");
        TR.put("You decide to...", "あなたはどうするか決める...");
        TR.put("Cut the comm link [Esc]", "通信リンクを切断する [Esc]");
        TR.put("Name:", "名前:");
        TR.put("Rank:", "階級:");
        TR.put("fleet", "艦隊");
        TR.put("Lieutenant", "中尉");
        TR.put("General", "将軍");
        TR.put("Establishing connection...", "接続を確立しています...");
        TR.put("Go back", "戻る");
        TR.put("Open the comm directory", "通信ディレクトリを開く");
'''

if 'TR.put("Open a comm link"' not in content:
    content = content.replace('TR.put("Campaign", "キャンペーン");', 'TR.put("Campaign", "キャンペーン");\n' + new_translations)

with open(r'.\source\com\applicationjp\JPTranslationPlugin.java', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated JPTranslationPlugin.java")
