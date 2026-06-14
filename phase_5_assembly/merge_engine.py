"""
Phase 5: Merge Engine (DETERMINISTIC - NO LLM)

Merges translated Japanese text back into the original application file
structures (CSV, JSON, .group), preserving all logic columns,
IDs, and non-translatable data.

Input:  data/chunks/phase4_approved.json  (from Phase 4 critic)
        Vanilla application files as structural templates
Output: Complete localized application files in the plugin folder
"""

import sys
import io
import os
import csv
import json
import copy
import shutil
from datetime import datetime, timezone

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = r"E:\lamesa\2026\application-jp"
VANILLA_DATA = r"C:\Program Files (x86)\Acme Corp\Application\application-core\data"
PLUGIN_DATA = os.path.join(PROJECT_ROOT, r"plugins\JP_Lang_Pack\data")
CHUNKS_FILE = os.path.join(PROJECT_ROOT, r"data\chunks\phase4_approved.json")
STATE_FILE = os.path.join(PROJECT_ROOT, r"core\state.json")

# Columns in rules.csv that must NEVER be pluginified
RULES_LOGIC_COLS = {"id", "trigger", "conditions", "script"}

# Translatable columns per known CSV file (only these get overwritten).
# Any column NOT listed here is treated as a logic/structural column.
# If a CSV file is not in this map, we fall back to translating all
# non-first-column (non-id) string columns present in the chunks.
TRANSLATABLE_COLS = {
    "campaign/rules.csv":                       {"text", "options"},
    "campaign/compluginities.csv":                 {"name", "desc"},
    "campaign/abilities.csv":                   {"name", "desc"},
    "campaign/industries.csv":                  {"name", "desc", "shortName"},
    "campaign/market_conditions.csv":           {"name", "desc", "shortName"},
    "campaign/reports.csv":                     {"subject", "summary", "assessment"},
    "campaign/special_items.csv":               {"name", "desc"},
    "campaign/submarkets.csv":                  {"name", "desc"},
    "campaign/procgen/name_gen_data.csv":        {"name"},
    "characters/person_names.csv":              {"name"},
    "characters/personalities.csv":             {"name", "desc"},
    "characters/skills/aptitude_data.csv":      {"name", "description"},
    "characters/skills/skill_data.csv":         {"name", "description", "author"},
    "hullplugins/hull_plugins.csv":                   {"name", "desc", "short", "sPluginDesc"},
    "hulls/ship_data.csv":                      {"name", "designation"},
    "hulls/wing_data.csv":                      {"role desc"},
    "shipsystems/ship_systems.csv":             {"name"},
    "strings/descriptions.csv":                 {"text1", "text2", "text3", "text4", "text5"},
    "weapons/weapon_data.csv":                  {"name", "primaryRoleStr", "customPrimary", "customPrimaryHL", "customAncillary", "customAncillaryHL"},
}


def normalize_path(p):
    """Normalize a file path to use forward slashes for consistent keying."""
    return p.replace("\\", "/")


def load_chunks(path):
    """
    Load the phase4_approved.json chunk file.

    Expected format: a flat dict with keys like:
        "source_file|row_key|column" -> "translated text"

    OR a list of dicts with fields:
        source_file, row_key, column, chunk_type, source_text, translation
    """
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    chunks = {}  # key: (source_file_norm, row_key, column) -> translation

    if isinstance(raw, dict):
        # Flat dict format: "source_file|row_key|column" -> translation
        for compound_key, translation in raw.items():
            parts = compound_key.split("|")
            if len(parts) >= 3:
                src = normalize_path(parts[0])
                row_key = parts[1]
                col = "|".join(parts[2:])  # column name (rejoin if | in col name)
                chunks[(src, row_key, col)] = translation
            else:
                print(f"  WARNING: Skipping malformed key: {compound_key}")

    elif isinstance(raw, list):
        # List-of-dicts format
        for item in raw:
            src = normalize_path(item["source_file"])
            row_key = item["row_key"]
            col = item["column"]
            if "translation" not in item:
                continue
            translation = item["translation"]
            chunks[(src, row_key, col)] = translation
    else:
        print("ERROR: Unrecognized chunk format in phase4_approved.json")
        sys.exit(1)

    return chunks


def group_by_source(chunks):
    """Group chunks by source_file -> { row_key -> { column -> translation } }."""
    grouped = {}
    for (src, row_key, col), translation in chunks.items():
        if src not in grouped:
            grouped[src] = {}
        if row_key not in grouped[src]:
            grouped[src][row_key] = {}
        grouped[src][row_key][col] = translation
    return grouped


# ---------------------------------------------------------------------------
# CSV Merge
# ---------------------------------------------------------------------------

def get_csv_id_column(header, source_file):
    """Determine which column is the row key for a given CSV file."""
    norm = normalize_path(source_file)
    # name_gen_data uses 'name' as the primary key component
    if "name_gen_data" in norm:
        return "name"
    # Most CSVs use 'id' as the first column
    if "id" in header:
        return "id"
    # Fall back to first column
    return header[0]


def merge_csv(source_file, row_translations, vanilla_path, output_path):
    """
    Merge translations into a CSV file.
    - Reads the vanilla CSV as the structural template
    - Overwrites ONLY translatable columns with Japanese text
    - Preserves all logic columns byte-for-byte
    """
    norm = normalize_path(source_file)
    is_rules = "rules.csv" in norm

    # Read vanilla file with UTF-8 first, fallback to CP1252
    # CRITICAL: Must use newline="" to prevent Python from silently converting \r\n to \n in backend logic strings
    try:
        with open(vanilla_path, "r", encoding="utf-8", newline="") as f:
            content = f.read()
    except UnicodeDecodeError:
        with open(vanilla_path, "r", encoding="cp1252", newline="") as f:
            content = f.read()

    # Strip BOM if present in vanilla (shouldn't be, but be safe)
    if content.startswith("\ufeff"):
        content = content[1:]

    reader = csv.reader(io.StringIO(content, newline=""))
    header = next(reader)
    rows = list(reader)

    id_col_name = get_csv_id_column(header, source_file)
    id_col_idx = header.index(id_col_name) if id_col_name in header else 0

    # Determine which columns are allowed to be translated
    allowed_cols = TRANSLATABLE_COLS.get(norm, None)

    # Track how many cells were updated
    cells_updated = 0

    # Build output rows
    output_rows = []
    for row in rows:
        if not row:
            output_rows.append(row)
            continue

        # Reconstruct composite keys matching extraction engine
        if "name_gen_data.csv" in norm:
            name_idx = header.index("name") if "name" in header else 0
            tags_idx = header.index("tags") if "tags" in header else len(header)
            name_val = row[name_idx] if name_idx < len(row) else ""
            tags_val = row[tags_idx] if tags_idx < len(row) else ""
            row_key = f"{name_val}|{tags_val}"
        elif "descriptions.csv" in norm:
            id_idx = header.index("id") if "id" in header else 0
            type_idx = header.index("type") if "type" in header else len(header)
            id_val = row[id_idx] if id_idx < len(row) else ""
            type_val = row[type_idx] if type_idx < len(row) else ""
            row_key = f"{id_val}|{type_val}"
        elif "reports.csv" in norm:
            type_idx = header.index("event_type") if "event_type" in header else 0
            stage_idx = header.index("event_stage") if "event_stage" in header else len(header)
            type_val = row[type_idx] if type_idx < len(row) else ""
            stage_val = row[stage_idx] if stage_idx < len(row) else ""
            row_key = f"{type_val}|{stage_val}"
        else:
            row_key = row[id_col_idx] if id_col_idx < len(row) else ""

        if row_key in row_translations:
            col_translations = row_translations[row_key]
            new_row = list(row)  # copy

            for col_name, translation in col_translations.items():
                if col_name not in header:
                    continue
                col_idx = header.index(col_name)

                # Safety: never touch logic columns in rules.csv
                if is_rules and col_name in RULES_LOGIC_COLS:
                    print(f"  WARNING: Skipping protected column '{col_name}' in rules.csv row '{row_key}'")
                    continue

                # Safety: only touch allowed columns if whitelist exists
                if allowed_cols is not None and col_name not in allowed_cols:
                    continue

                original_text = row[col_idx] if col_idx < len(row) else ""
                if is_rules and col_name == "options" and "\r\n" in original_text and "\r\n" not in translation:
                    import re
                    orig_keys = []
                    for line in original_text.split("\r\n"):
                        if ":" in line:
                            parts = line.split(":")
                            key = ":".join(parts[:-1]) + ":"
                            if key.strip():
                                orig_keys.append(key.strip())
                    
                    fixed_translation = translation
                    for key in orig_keys:
                        # Escape regex and make sure we don't replace if it already has \r\n
                        escaped_key = re.escape(key)
                        fixed_translation = re.sub(r'(?<!^)(?<!\r\n)(?<!\n)(' + escaped_key + r')', r'\r\n\1', fixed_translation)
                    translation = fixed_translation.strip()

                # Pad row if needed
                while len(new_row) <= col_idx:
                    new_row.append("")

                new_row[col_idx] = translation
                cells_updated += 1

            output_rows.append(new_row)
        else:
            output_rows.append(list(row))

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write output CSV - NO BOM, preserve actual newlines
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        for row in output_rows:
            writer.writerow(row)

    return cells_updated


# ---------------------------------------------------------------------------
# JSON / .group Merge
# ---------------------------------------------------------------------------

def set_nested_value(obj, path_parts, value):
    """
    Set a value in a nested dict/list structure using path parts.
    Path parts are dot-separated keys, with list indices as integers.
    Example: ["names", "ships", "0"] sets obj["names"]["ships"][0]
    """
    for i, part in enumerate(path_parts[:-1]):
        if isinstance(obj, list):
            try:
                idx = int(part)
                obj = obj[idx]
            except (ValueError, IndexError):
                return False
        elif isinstance(obj, dict):
            if part in obj:
                obj = obj[part]
            else:
                return False
        else:
            return False

    # Set the final value
    last = path_parts[-1]
    if isinstance(obj, list):
        try:
            idx = int(last)
            obj[idx] = value
            return True
        except (ValueError, IndexError):
            return False
    elif isinstance(obj, dict):
        obj[last] = value
        return True
    return False


def quote_bare_keys(text):
    import re
    bare_key_re = re.compile(r'^(\s*)([a-zA-Z_][a-zA-Z0-9_]*)(\s*:\s*)')
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or stripped.startswith('"') or stripped[0] in "]}),":
            result.append(line)
            continue
        m = bare_key_re.match(line)
        if m:
            leading = m.group(1)
            key = m.group(2)
            colon = m.group(3)
            rest = line[m.end():]
            line = f'{leading}"{key}"{colon}{rest}'
        result.append(line)
    return "\n".join(result)

def parse_json_tolerant(path):
    """
    Parse a JSON/HJSON file, stripping comments, trailing commas, bare keys, and float suffixes.
    """
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip BOM
    if content.startswith("\ufeff"):
        content = content[1:]

    # Remove single-line comments (# style used by Application)
    lines = content.split("\n")
    cleaned = []
    for line in lines:
        in_string = False
        escape = False
        result = []
        for ch in line:
            if escape:
                result.append(ch)
                escape = False
                continue
            if ch == "\\":
                escape = True
                result.append(ch)
                continue
            if ch == '"':
                in_string = not in_string
                result.append(ch)
                continue
            if ch == "#" and not in_string:
                break
            result.append(ch)
        cleaned.append("".join(result))

    text = "\n".join(cleaned)

    # Remove trailing commas before } or ]
    import re
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # Strip trailing commas and whitespace from the end of the file
    text = text.strip()
    if text.endswith(','):
        text = text[:-1].strip()

    # Remove float suffixes
    text = re.sub(r'\b(\d+\.?\d*)f\b', r'\1', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    quoted = quote_bare_keys(text)
    return json.loads(quoted)


def parse_bracket_path(path_str):
    import re
    # Matches keys inside quotes or indices: e.g. ['key'] or [0]
    tokens = re.findall(r"\'([^\']+)\'|(\d+)", path_str)
    parts = []
    for t in tokens:
        if t[0]:
            parts.append(t[0])
        else:
            # Cast list indices to integers so set_nested_value works correctly
            parts.append(int(t[1]))
    return parts


def merge_json(source_file, row_translations, vanilla_path, output_path):
    """
    Merge translations into a JSON or .group file.
    - Deep copies the vanilla structure
    - Replaces values at specified json_paths
    - row_key is the json_path (bracket notation or dot-separated)
    - column is typically 'value' or the specific field name
    """
    data = parse_json_tolerant(vanilla_path)

    fields_updated = 0
    norm = normalize_path(source_file)
    group_id = os.path.splitext(os.path.basename(source_file))[0]

    for json_path, col_translations in row_translations.items():
        # Strip group_id prefix for group files (e.g. hegemony.displayName -> displayName)
        actual_path = json_path
        if norm.endswith(".group") and actual_path.startswith(group_id + "."):
            actual_path = actual_path[len(group_id) + 1:]

        # Resolve path parts based on bracket notation vs dot notation
        if actual_path.startswith("["):
            path_parts = parse_bracket_path(actual_path)
        else:
            path_parts = [int(p) if p.isdigit() else p for p in actual_path.split(".")]

        # For JSON chunks, the "column" is typically the field name or "value"
        for col_name, translation in col_translations.items():
            # If column name matches the full path, stripped path, or "value"
            if col_name == json_path or col_name == actual_path or col_name == "value":
                if set_nested_value(data, path_parts, translation):
                    fields_updated += 1
            else:
                # Column name is appended to the path
                full_path = path_parts + [col_name]
                if set_nested_value(data, full_path, translation):
                    fields_updated += 1

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Write output JSON - NO BOM
    with open(output_path, "w", encoding="utf-8", newline="") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return fields_updated


# ---------------------------------------------------------------------------
# State management
# ---------------------------------------------------------------------------

def update_state(files_merged, files_detail):
    """Update state.json with merge results."""
    if not os.path.exists(STATE_FILE):
        print(f"WARNING: State file not found at {STATE_FILE}")
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    state["current_phase"] = 5
    state["phases"]["5_assembly"] = {
        "status": "completed",
        "files_merged": files_merged,
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "files": files_detail,
    }

    with open(STATE_FILE, "w", encoding="utf-8", newline="") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"\nUpdated state.json: phase 5_assembly = completed, {files_merged} files merged")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("Phase 5: Merge Engine")
    print("=" * 70)

    # --- Load chunks ---
    if not os.path.exists(CHUNKS_FILE):
        print(f"\nERROR: Chunks file not found: {CHUNKS_FILE}")
        print("Phase 4 (critic) must complete before running Phase 5.")
        print("Expected file: data/chunks/phase4_approved.json")
        sys.exit(1)

    print(f"\nLoading chunks from: {CHUNKS_FILE}")
    chunks = load_chunks(CHUNKS_FILE)
    print(f"  Loaded {len(chunks)} translation chunks")

    if not chunks:
        print("  No chunks to merge. Exiting.")
        update_state(0, [])
        return

    # --- Group by source file ---
    grouped = group_by_source(chunks)
    print(f"  Grouped into {len(grouped)} source files")

    # --- Process each source file ---
    files_merged = 0
    files_detail = []
    total_cells = 0
    errors = []

    for source_file in sorted(grouped.keys()):
        row_translations = grouped[source_file]
        norm = normalize_path(source_file)

        # Determine vanilla source path
        vanilla_path = os.path.join(VANILLA_DATA, norm.replace("/", os.sep))
        if not os.path.exists(vanilla_path):
            msg = f"  WARNING: Vanilla file not found: {vanilla_path}"
            print(msg)
            errors.append(msg)
            continue

        # Determine output path
        output_path = os.path.join(PLUGIN_DATA, norm.replace("/", os.sep))

        # Determine file type and merge accordingly
        ext = os.path.splitext(norm)[1].lower()

        try:
            if ext == ".csv":
                cells = merge_csv(source_file, row_translations, vanilla_path, output_path)
                total_cells += cells
                print(f"  [CSV]     {norm}: {cells} cells updated ({len(row_translations)} rows)")
                files_detail.append({
                    "file": norm,
                    "type": "csv",
                    "cells_updated": cells,
                    "rows_touched": len(row_translations),
                })

            elif ext in (".json", ".group"):
                fields = merge_json(source_file, row_translations, vanilla_path, output_path)
                total_cells += fields
                label = "FACTION" if ext == ".group" else "JSON"
                print(f"  [{label}]  {norm}: {fields} fields updated")
                files_detail.append({
                    "file": norm,
                    "type": ext.lstrip("."),
                    "fields_updated": fields,
                })

            else:
                msg = f"  WARNING: Unknown file type '{ext}' for {norm}, skipping"
                print(msg)
                errors.append(msg)
                continue

            files_merged += 1

        except Exception as e:
            msg = f"  ERROR processing {norm}: {e}"
            print(msg)
            errors.append(msg)

    # --- Summary ---
    print("\n" + "=" * 70)
    print("Merge Summary")
    print("=" * 70)
    print(f"  Files merged:       {files_merged}")
    print(f"  Total cells/fields: {total_cells}")
    print(f"  Translation chunks: {len(chunks)}")
    if errors:
        print(f"  Errors/warnings:    {len(errors)}")
        for err in errors:
            print(f"    {err}")

    # --- Update state ---
    update_state(files_merged, files_detail)

    print("\nPhase 5 complete.")


if __name__ == "__main__":
    main()
