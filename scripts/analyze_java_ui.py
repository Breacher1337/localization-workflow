import re
import json
import os

def analyze_file(filepath):
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return []

    try:
        with open(filepath, "rb") as f:
            content = f.read().decode('utf-16')
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

    templates = []

    # Improved regex for variable assignments with concatenations
    # Handles multiline and complex expressions better
    concat_re = re.compile(r'String\s+(\w+)\s*=\s*([^;]+);')

    ui_methods = ["addPara", "addParagraph", "getString", "setText", "addMessage"]
    ui_re = re.compile(r'(\w+)\.(' + '|'.join(ui_methods) + r')\(([^,)]+)')

    lines = content.splitlines()
    vars_map = {}

    for i, line in enumerate(lines):
        line = line.strip()
        # Look for concatenations
        m_concat = concat_re.search(line)
        if m_concat:
            var_name = m_concat.group(1)
            expr = m_concat.group(2).strip()
            if '+' in expr:
                vars_map[var_name] = expr

        # Look for UI usage
        m_ui = ui_re.search(line)
        if m_ui:
            obj_name = m_ui.group(1)
            method = m_ui.group(2)
            arg = m_ui.group(3).strip()

            # Trace back if it's a variable
            expr_to_tokenize = None
            if arg in vars_map:
                expr_to_tokenize = vars_map[arg]
            elif '"' in arg and '+' in arg:
                expr_to_tokenize = arg

            if expr_to_tokenize:
                template_data = tokenize_expression(expr_to_tokenize)
                if template_data:
                    templates.append({
                        "object": obj_name,
                        "method": method,
                        "original_expression": expr_to_tokenize,
                        "template": template_data['template'],
                        "regex": template_data['regex'],
                        "context": line
                    })

    return templates

def tokenize_expression(expr):
    # Splits by +, but ignores + inside quotes
    parts = []
    current = ""
    in_quotes = False
    for char in expr:
        if char == '"':
            in_quotes = not in_quotes
            current += char
        elif char == '+' and not in_quotes:
            parts.append(current.strip())
            current = ""
        else:
            current += char
    parts.append(current.strip())

    template = ""
    regex_parts = []
    token_idx = 0
    has_literal = False

    for part in parts:
        if part.startswith('"') and part.endswith('"'):
            literal = part[1:-1]
            # Escape for template (though likely fine)
            template += literal
            # Escape for regex
            regex_parts.append(re.escape(literal))
            has_literal = True
        else:
            template += "{" + str(token_idx) + "}"
            # For regex, matching anything (reluctant)
            regex_parts.append("(.*?)")
            token_idx += 1

    if token_idx == 0 and not has_literal:
        return None

    # We only care about templates that have at least some literal text
    if not has_literal:
        return None

    return {
        "template": template,
        "regex": "^" + "".join(regex_parts) + "$"
    }

if __name__ == "__main__":
    results = analyze_file("java_tools/src/button_decompiled.java")
    # Dedup by template
    unique_templates = {}
    for r in results:
        unique_templates[r['template']] = r

    os.makedirs("data", exist_ok=True)
    with open("data/extracted_templates.json", "w", encoding="utf-8") as f:
        json.dump(list(unique_templates.values()), f, indent=2, ensure_ascii=False)
    print(f"Extracted {len(unique_templates)} unique templates to data/extracted_templates.json")
