import csv

vanilla_file = r"C:\Program Files (x86)\Acme Corp\Application\application-core\data\campaign\rules.csv"
plugin_file = r"e:\lamesa\2026\application-jp\plugins\JP_Lang_Pack\data\campaign\rules.csv"

def get_row(filepath, target_id):
    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0] == target_id:
                return row
    return None

v_row = get_row(vanilla_file, "TTmarketWeirdPlugins5")
m_row = get_row(plugin_file, "TTmarketWeirdPlugins5")

print("Vanilla len:", len(v_row) if v_row else None)
print("Plugin len:", len(m_row) if m_row else None)
if m_row:
    print("Plugin row structure (lengths of items):", [len(x) for x in m_row])
