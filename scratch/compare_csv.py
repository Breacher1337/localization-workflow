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

print("Vanilla:")
print(v_row)
print("Plugin:")
print(m_row)

print("Vanilla len:", len(v_row))
print("Plugin len:", len(m_row))
