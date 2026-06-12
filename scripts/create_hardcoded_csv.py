import sys
import os
import config
﻿import csv
import os

plugin_dir = config.APPLICATION_CORE_DIR
os.makedirs(plugin_dir, exist_ok=True)
csv_path = os.path.join(plugin_dir, "hardcoded_ui.csv")

translations = [
    ("english", "japanese"),
    ("Continue", "続きから"),
    ("Tutorials", "チュートリアル"),
    ("Missions", "ミッション"),
    ("New Application", "新規アプリケーション"),
    ("Load Application", "データ読み込み"),
    ("Codex", "データベース"),
    ("Settings", "設定"),
    ("Credits", "クレジット"),
    ("Quit", "システム停止"),
    ("Tutorial", "チュートリアル"),
    ("Campaign", "キャンペーン"),
    ("Open a comm link", "通信リンクを開く"),
    ("You decide to...", "あなたはどうするか決める..."),
    ("Cut the comm link [Esc]", "通信リンクを切断する [Esc]"),
    ("Name:", "名前:"),
    ("Rank:", "階級:"),
    ("fleet", "艦隊"),
    ("Lieutenant", "中尉"),
    ("General", "将軍"),
    ("Establishing connection...", "接続を確立しています..."),
    ("Go back", "戻る"),
    ("Open the comm directory", "通信ディレクトリを開く")
]

with open(csv_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(translations)

print(f"Created {csv_path}")
