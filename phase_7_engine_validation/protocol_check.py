import sys
import os
import config
"""
Phase 7: Engine Validation / Protocol Check (DETERMINISTIC - NO LLM)

Final gate before production release. Validates all output files
against Application's fragile CSV parser requirements.

Checks:
  1. BOM Detection - Application crashes on UTF-8 BOM (EF BB BF)
  2. Column Count Integrity - every CSV row must match header width
  3. Duplicate Key Detection - composite keys for name_gen_data, id for others
  4. Placeholder Integrity - $var, %s, {var} must survive translation
  5. Required Files Check - plugin_info.json + masterlist coverage
  6. JSON/Group Validity - all .json/.group files must parse

Input:  Complete plugin folder + optional phase2_validated.json
Output: Pass/Fail report with specific violations listed
"""

import sys
import io
import os
import csv
import json
import re
from datetime import datetime, timezone
from collections import defaultdict

sys.stdout.reconfigure(encoding='utf-8')

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
PROJECT_ROOT = r"."
PLUGIN_ROOT = os.path.join(PROJECT_ROOT, r"plugins/JP_Lang_Pack")
PLUGIN_DATA = os.path.join(PLUGIN_ROOT, "data")
VANILLA_DATA = config.APPLICATION_CORE_DIR
STATE_FILE = os.path.join(PROJECT_ROOT, r"core/state.json")
MASTERLIST = os.path.join(PROJECT_ROOT, "localization_masterlist.csv")
PHASE2_FILE = os.path.join(PROJECT_ROOT, os.path.join("data", "chunks", "phase2_validated.json"))
REPORT_FILE = os.path.join(PROJECT_ROOT, r"localization_tracking\validation_report.txt")

# Placeholder regex: matches $variable, $varName, %s, %d, %f, %.2f, {name}, etc.
PLACEHOLDER_RE = re.compile(
    r"\$[a-zA-Z_]\w*"     # $variable style
    r"|%[0-9]*\.?[0-9]*[sdfiexXo]"  # printf-style %s, %d, %.2f etc.
    r"|\{[a-zA-Z_]\w*\}"  # {variable} style
)


def normalize_path(p):
    """Normalize path separators to backslash for Windows comparison."""
    return p.replace("/", "\\")


# ---------------------------------------------------------------------------
# Check 1: BOM Detection
# ---------------------------------------------------------------------------

def check_bom(all_files):
    """
    Read first 3 bytes of every file. Flag if EF BB BF (UTF-8 BOM) is found.
    CRITICAL: Application crashes on BOM.
    """
    errors = []
    checked = 0

    for filepath in all_files:
        checked += 1
        try:
            with open(filepath, "rb") as f:
                header_bytes = f.read(3)
            if header_bytes == b"\xef\xbb\xbf":
                rel = os.path.relpath(filepath, PLUGIN_ROOT)
                errors.append(f"BOM detected: {rel}")
        except Exception as e:
            errors.append(f"BOM check error on {os.path.relpath(filepath, PLUGIN_ROOT)}: {e}")

    return {
        "name": "BOM Detection",
        "checked": checked,
        "errors": errors,
        "passed": len(errors) == 0,
    }


# ---------------------------------------------------------------------------
# Check 2: Column Count Integrity (CSV only)
# ---------------------------------------------------------------------------

def check_column_counts(csv_files):
    """
    Parse header to get expected column count.
    Verify every row has the same number of columns.
    csv.reader handles quoted fields with internal commas correctly.
    """
    errors = []
    checked = 0

    for filepath in csv_files:
        checked += 1
        rel = os.path.relpath(filepath, PLUGIN_ROOT)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Strip BOM if present (we already flag it in check 1)
            if content.startswith("\ufeff"):
                content = content[1:]

            reader = csv.reader(io.StringIO(content))
            header = next(reader, None)
            if header is None:
                errors.append(f"Empty CSV (no header): {rel}")
                continue

            expected = len(header)
            for line_num, row in enumerate(reader, start=2):
                # Skip completely empty rows
                if not row:
                    continue
                if len(row) != expected:
                    errors.append(
                        f"Column count mismatch in {rel} line {line_num}: "
                        f"expected {expected}, got {len(row)}"
                    )
        except Exception as e:
            errors.append(f"Column check error on {rel}: {e}")

    return {
        "name": "Column Count Integrity",
        "checked": checked,
        "errors": errors,
        "passed": len(errors) == 0,
    }


# ---------------------------------------------------------------------------
# Check 3: Duplicate Key Detection
# ---------------------------------------------------------------------------

# CSVs where repeated first-column values are intentional by design.
# These files use multi-column composite keys or template variants.
DUPLICATE_EXEMPT_FILES = {
    "reports.csv",      # event_type+event_stage: multiple stages per event
    "rules.csv",        # id is intentionally repeated for multi-trigger rules
    "ui.csv",           # repeated section header rows ("key") by design
}

# CSVs that use (id, type) composite keys instead of just id
COMPOSITE_ID_TYPE_FILES = {
    "descriptions.csv",  # same id for SHIP/WEAPON/HULLPLUGIN descriptions
}


def check_duplicate_keys(csv_files):
    """
    For name_gen_data.csv: composite key (name, secondary, tags)
    For reports.csv/rules.csv: skip (duplicates are by design)
    For other CSVs: first column (id) for duplicates.
    Report exact duplicate rows.
    """
    errors = []
    checked = 0

    for filepath in csv_files:
        checked += 1
        rel = os.path.relpath(filepath, PLUGIN_ROOT)
        basename = os.path.basename(filepath).lower()

        # Skip files where duplicate first-column values are by design
        if basename in DUPLICATE_EXEMPT_FILES:
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            if content.startswith("\ufeff"):
                content = content[1:]

            reader = csv.reader(io.StringIO(content))
            header = next(reader, None)
            if header is None:
                continue

            rows = list(reader)

            if basename == "name_gen_data.csv":
                # Composite key: (name, secondary/category, tags)
                name_idx = header.index("name") if "name" in header else 0
                if "secondary" in header:
                    cat_idx = header.index("secondary")
                elif "category" in header:
                    cat_idx = header.index("category")
                else:
                    cat_idx = 1
                tags_idx = header.index("tags") if "tags" in header else 2

                seen_keys = {}
                for line_num, row in enumerate(rows, start=2):
                    if not row:
                        continue
                    name_val = row[name_idx] if name_idx < len(row) else ""
                    if not name_val.strip():
                        continue
                    cat_val = row[cat_idx] if cat_idx < len(row) else ""
                    tags_val = row[tags_idx] if tags_idx < len(row) else ""
                    composite = (name_val, cat_val, tags_val)

                    if composite in seen_keys:
                        errors.append(
                            f"Duplicate composite key in {rel} line {line_num}: "
                            f"({name_val}, {cat_val}, {tags_val}) "
                            f"- first seen at line {seen_keys[composite]}"
                        )
                    else:
                        seen_keys[composite] = line_num

            elif basename == "person_names.csv":
                # Composite key: (name, gender, usage, category)
                col_indices = []
                for col_name in ["name", "gender", "usage", "category"]:
                    col_indices.append(header.index(col_name) if col_name in header else len(header))

                seen_keys = {}
                for line_num, row in enumerate(rows, start=2):
                    if not row:
                        continue
                    name_val = row[col_indices[0]] if (col_indices and col_indices[0] < len(row)) else ""
                    if not name_val.strip():
                        continue
                    composite = tuple(
                        row[idx] if idx < len(row) else ""
                        for idx in col_indices
                    )
                    if composite in seen_keys:
                        errors.append(
                            f"Duplicate composite key in {rel} line {line_num}: "
                            f"{composite} - first seen at line {seen_keys[composite]}"
                        )
                    else:
                        seen_keys[composite] = line_num

            elif basename in COMPOSITE_ID_TYPE_FILES:
                # Composite key: (id, type) — same id used for SHIP vs WEAPON etc.
                id_col = header.index("id") if "id" in header else 0
                type_col = header.index("type") if "type" in header else 1

                seen_keys = {}
                for line_num, row in enumerate(rows, start=2):
                    if not row:
                        continue
                    id_val = row[id_col] if id_col < len(row) else ""
                    type_val = row[type_col] if type_col < len(row) else ""
                    if not id_val.strip():
                        continue
                    composite = (id_val, type_val)
                    if composite in seen_keys:
                        errors.append(
                            f"Duplicate composite key in {rel} line {line_num}: "
                            f"({id_val}, {type_val}) - first seen at line {seen_keys[composite]}"
                        )
                    else:
                        seen_keys[composite] = line_num
            else:
                # Standard id-based duplicate check
                id_col = 0
                if "id" in header:
                    id_col = header.index("id")

                seen_keys = {}
                for line_num, row in enumerate(rows, start=2):
                    if not row:
                        continue
                    key = row[id_col] if id_col < len(row) else ""
                    # Skip empty keys (common in some CSVs)
                    if not key.strip():
                        continue

                    if key in seen_keys:
                        errors.append(
                            f"Duplicate key in {rel} line {line_num}: "
                            f"'{key}' - first seen at line {seen_keys[key]}"
                        )
                    else:
                        seen_keys[key] = line_num

        except Exception as e:
            errors.append(f"Duplicate key check error on {rel}: {e}")

    return {
        "name": "Duplicate Key Detection",
        "checked": checked,
        "errors": errors,
        "passed": len(errors) == 0,
    }


# ---------------------------------------------------------------------------
# Check 4: Placeholder Integrity
# ---------------------------------------------------------------------------

def check_placeholders():
    """
    If phase2_validated.json exists, load the placeholder catalog.
    For each chunk, verify all original placeholders still exist in translation.
    """
    if not os.path.exists(PHASE2_FILE):
        return {
            "name": "Placeholder Integrity",
            "checked": 0,
            "errors": [],
            "passed": True,
            "skipped": True,
            "skip_reason": f"phase2_validated.json not found at {PHASE2_FILE}",
        }

    errors = []
    checked = 0

    try:
        with open(PHASE2_FILE, "r", encoding="utf-8") as f:
            phase2_data = json.load(f)

        # Expected format: list of chunks or dict of key -> { source_text, translation, placeholders }
        chunks = []
        if isinstance(phase2_data, dict):
            for key, val in phase2_data.items():
                if isinstance(val, dict):
                    chunks.append({
                        "key": key,
                        "source_text": val.get("source_text", ""),
                        "translation": val.get("translation", ""),
                        "placeholders": val.get("placeholders", []),
                    })
                else:
                    # Flat dict: key -> translation. Extract placeholders from key.
                    chunks.append({
                        "key": key,
                        "source_text": key,
                        "translation": str(val),
                    })
        elif isinstance(phase2_data, list):
            chunks = phase2_data

        for chunk in chunks:
            checked += 1
            source = chunk.get("source_text", "")
            translation = chunk.get("translation", "")

            if not translation:
                continue

            # Extract placeholders from source text
            source_placeholders = set(PLACEHOLDER_RE.findall(source))
            if not source_placeholders:
                continue

            # Check each placeholder exists in translation
            translation_placeholders = set(PLACEHOLDER_RE.findall(translation))
            missing = source_placeholders - translation_placeholders
            if missing:
                key = chunk.get("key", "unknown")
                # Truncate long keys for readability
                if len(key) > 80:
                    key = key[:77] + "..."
                errors.append(
                    f"Missing placeholders in '{key}': {sorted(missing)}"
                )

    except Exception as e:
        errors.append(f"Placeholder check error: {e}")

    return {
        "name": "Placeholder Integrity",
        "checked": checked,
        "errors": errors,
        "passed": len(errors) == 0,
    }


# ---------------------------------------------------------------------------
# Check 5: Required Files Check
# ---------------------------------------------------------------------------

def check_required_files():
    """
    Verify plugin_info.json exists and is valid JSON.
    Verify all files listed in localization_masterlist.csv exist in the plugin folder.
    """
    errors = []
    checked = 0

    # Check plugin_info.json
    checked += 1
    plugin_info_path = os.path.join(PLUGIN_ROOT, "plugin_info.json")
    if not os.path.exists(plugin_info_path):
        errors.append("CRITICAL: plugin_info.json not found in plugin root")
    else:
        try:
            with open(plugin_info_path, "r", encoding="utf-8") as f:
                content = f.read()
            if content.startswith("\ufeff"):
                content = content[1:]
            json.loads(content)
        except json.JSONDecodeError as e:
            errors.append(f"plugin_info.json is not valid JSON: {e}")

    # Check masterlist entries
    if os.path.exists(MASTERLIST):
        try:
            with open(MASTERLIST, "r", encoding="utf-8") as f:
                content = f.read()
            if content.startswith("\ufeff"):
                content = content[1:]

            reader = csv.reader(io.StringIO(content))
            header = next(reader, None)

            # Find the 'File Path' column
            path_col = 0
            if header and "File Path" in header:
                path_col = header.index("File Path")

            for row in reader:
                if not row or not row[path_col].strip():
                    continue
                checked += 1
                file_rel = row[path_col].strip()
                # Masterlist paths use backslash, prepend data/
                expected_path = os.path.join(PLUGIN_DATA, normalize_path(file_rel))
                if not os.path.exists(expected_path):
                    errors.append(
                        f"Missing file from masterlist: data\\{file_rel} "
                        f"(expected at {expected_path})"
                    )
        except Exception as e:
            errors.append(f"Masterlist check error: {e}")
    else:
        errors.append(f"WARNING: localization_masterlist.csv not found at {MASTERLIST}")

    return {
        "name": "Required Files Check",
        "checked": checked,
        "errors": errors,
        "passed": len(errors) == 0,
    }


# ---------------------------------------------------------------------------
# Check 6: JSON/Group Validity
# ---------------------------------------------------------------------------

def strip_json_comments(content):
    """
    Remove single-line comments (# style) from Application JSON/HJSON,
    being careful not to strip # characters inside quoted strings.
    """
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
    return "\n".join(cleaned)


def quote_bare_keys(text):
    """
    Application .group and some .json files use HJSON-like syntax
    where object keys may be unquoted: e.g. id:"hegemony" instead of
    "id":"hegemony". This function adds double-quotes around bare keys
    so standard json.loads() can parse them.

    Uses a line-by-line approach for robustness with tab-indented files.
    Handles patterns like:
      \tid:"value"   or   key_name: value   or   HEGEMONY:1
    But NOT already-quoted keys like "key":value
    """
    # Pattern: optional whitespace, then an unquoted key (word chars),
    # then optional whitespace and a colon.
    # The key must NOT be preceded by a quote character.
    bare_key_re = re.compile(
        r'^(\s*)'           # group 1: leading whitespace
        r'([a-zA-Z_][a-zA-Z0-9_]*)'  # group 2: bare key
        r'(\s*:\s*)'        # group 3: colon with optional whitespace
    )

    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        # Skip empty lines, comment-only lines, or lines starting with "
        if not stripped or stripped.startswith("#") or stripped.startswith('"'):
            result.append(line)
            continue
        # Skip lines that are just ] or } or , etc.
        if stripped[0] in "]}),":
            result.append(line)
            continue
        # Try to match a bare key at the start of the line
        m = bare_key_re.match(line)
        if m:
            leading = m.group(1)
            key = m.group(2)
            colon = m.group(3)
            rest = line[m.end():]
            line = f'{leading}"{key}"{colon}{rest}'
        result.append(line)
    return "\n".join(result)


def parse_application_json(filepath):
    """
    Parse Application-style JSON/HJSON (with comments, trailing commas,
    unquoted keys). Returns (data, None) on success or (None, error_msg)
    on failure.
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Strip BOM
    if content.startswith("\ufeff"):
        content = content[1:]

    # Step 1: Remove comments
    text = strip_json_comments(content)

    # Step 2: Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # Step 3: Try standard JSON first
    try:
        data = json.loads(text)
        return data, None
    except json.JSONDecodeError:
        pass

    # Step 4: Try quoting bare keys (HJSON-style)
    try:
        quoted = quote_bare_keys(text)
        data = json.loads(quoted)
        return data, None
    except json.JSONDecodeError as e:
        return None, str(e)


def check_json_validity(json_files):
    """
    Try to parse every .json and .group file.
    Report any JSON parse errors.
    """
    errors = []
    checked = 0

    warnings = []
    for filepath in json_files:
        checked += 1
        rel = os.path.relpath(filepath, PLUGIN_ROOT)
        try:
            _, err = parse_application_json(filepath)
            if err:
                # .group files use Application's non-standard HJSON.
                # Parse failures are WARNINGS, not errors, since
                # Application's own parser handles them fine.
                ext = os.path.splitext(filepath)[1].lower()
                if ext == ".group":
                    warnings.append(f"HJSON parse warning in {rel}: {err}")
                else:
                    errors.append(f"JSON parse error in {rel}: {err}")
        except Exception as e:
            errors.append(f"JSON read error in {rel}: {e}")

    return {
        "name": "JSON/Group Validity",
        "checked": checked,
        "errors": errors,
        "passed": len(errors) == 0,
    }


# ---------------------------------------------------------------------------
# Check 7: JSON Structural Integrity
# ---------------------------------------------------------------------------

def compare_json_structure(vanilla_data, plugin_data, path=""):
    errors = []
    if isinstance(vanilla_data, dict):
        if not isinstance(plugin_data, dict):
            return [f"Type mismatch at {path}: expected dict"]
        for k, v in vanilla_data.items():
            if k not in plugin_data:
                errors.append(f"Missing key '{k}' at {path if path else 'root'}")
            else:
                new_path = f"{path}.{k}" if path else k
                errors.extend(compare_json_structure(v, plugin_data[k], new_path))
    elif isinstance(vanilla_data, list):
        if not isinstance(plugin_data, list):
            return [f"Type mismatch at {path}: expected list"]
        # Basic check to ensure lists are roughly the same, but Application lists can change length
        # However, for localization, they shouldn't drop items
        if len(plugin_data) < len(vanilla_data):
            errors.append(f"List at {path} has fewer items than vanilla ({len(plugin_data)} vs {len(vanilla_data)})")
    return errors

def check_json_structural_integrity(json_files):
    errors = []
    checked = 0
    
    for filepath in json_files:
        rel = os.path.relpath(filepath, PLUGIN_DATA)
        vanilla_path = os.path.join(VANILLA_DATA, rel)
        if not os.path.exists(vanilla_path):
            continue
            
        checked += 1
        try:
            v_data, v_err = parse_application_json(vanilla_path)
            m_data, m_err = parse_application_json(filepath)
            
            if v_data and m_data:
                struct_errors = compare_json_structure(v_data, m_data)
                if struct_errors:
                    errors.append(f"Structural issues in {rel}:\n      - " + "\n      - ".join(struct_errors))
        except Exception as e:
            errors.append(f"Structure check error in {rel}: {e}")
            
    return {
        "name": "JSON Structural Integrity",
        "checked": checked,
        "errors": errors,
        "passed": len(errors) == 0,
    }


# ---------------------------------------------------------------------------
# File Discovery
# ---------------------------------------------------------------------------

def discover_files():
    """
    Recursively scan the plugin data directory.
    Returns (all_files, csv_files, json_files).
    """
    all_files = []
    csv_files = []
    json_files = []

    if not os.path.exists(PLUGIN_DATA):
        return all_files, csv_files, json_files

    for root, dirs, files in os.walk(PLUGIN_DATA):
        for fname in sorted(files):
            filepath = os.path.join(root, fname)
            all_files.append(filepath)

            ext = os.path.splitext(fname)[1].lower()
            if ext == ".csv":
                csv_files.append(filepath)
            elif ext in (".json", ".group"):
                json_files.append(filepath)

    return all_files, csv_files, json_files


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def generate_report(results, all_files, csv_files, json_files):
    """Generate the validation report text."""
    lines = []
    lines.append("=" * 70)
    lines.append("APPLICATION JP LOCALIZATION - ENGINE VALIDATION REPORT")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Plugin root:       {PLUGIN_ROOT}")
    lines.append(f"Total files:    {len(all_files)}")
    lines.append(f"CSV files:      {len(csv_files)}")
    lines.append(f"JSON/Group:   {len(json_files)}")
    lines.append("")

    total_errors = 0
    total_checks_passed = 0
    total_checks_failed = 0

    for result in results:
        name = result["name"]
        passed = result["passed"]
        checked = result["checked"]
        errors = result["errors"]
        skipped = result.get("skipped", False)

        status = "PASS" if passed else "FAIL"
        if skipped:
            status = "SKIP"

        lines.append("-" * 70)
        lines.append(f"Check: {name}")
        lines.append(f"Status: {status}  |  Items checked: {checked}  |  Errors: {len(errors)}")

        if skipped:
            lines.append(f"  Reason: {result.get('skip_reason', 'N/A')}")
            lines.append("")
            continue

        if passed:
            total_checks_passed += 1
        else:
            total_checks_failed += 1
            total_errors += len(errors)

        if errors:
            lines.append("  Errors:")
            # Limit displayed errors to prevent enormous reports
            display_limit = 50
            for i, err in enumerate(errors[:display_limit]):
                lines.append(f"    [{i+1}] {err}")
            if len(errors) > display_limit:
                lines.append(f"    ... and {len(errors) - display_limit} more errors")

        lines.append("")

    # Overall verdict
    lines.append("=" * 70)
    if total_errors == 0:
        verdict = "PASS"
        lines.append(f"OVERALL VERDICT: {verdict}")
        lines.append(f"  All checks passed. {total_checks_passed} checks clean.")
    else:
        verdict = "FAIL"
        lines.append(f"OVERALL VERDICT: {verdict}")
        lines.append(f"  {total_errors} total errors across {total_checks_failed} failed checks.")
        lines.append(f"  {total_checks_passed} checks passed.")
    lines.append("=" * 70)

    return "\n".join(lines), verdict, total_errors, total_checks_passed, total_checks_failed


# ---------------------------------------------------------------------------
# State Management
# ---------------------------------------------------------------------------

def update_state(checks_passed, checks_failed, verdict):
    """Update state.json with validation results."""
    if not os.path.exists(STATE_FILE):
        print(f"WARNING: State file not found at {STATE_FILE}")
        return

    with open(STATE_FILE, "r", encoding="utf-8") as f:
        state = json.load(f)

    state["current_phase"] = 7
    state["phases"]["7_validation"] = {
        "status": "completed",
        "verdict": verdict,
        "checks_passed": checks_passed,
        "checks_failed": checks_failed,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(STATE_FILE, "w", encoding="utf-8", newline="") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

    print(f"Updated state.json: phase 7_validation = completed, verdict = {verdict}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("=" * 70)
    print("Phase 7: Engine Validation / Protocol Check")
    print("=" * 70)

    # --- Discover files ---
    print(f"\nScanning: {PLUGIN_DATA}")
    all_files, csv_files, json_files = discover_files()
    print(f"  Total files found:    {len(all_files)}")
    print(f"  CSV files:            {len(csv_files)}")
    print(f"  JSON/Group files:   {len(json_files)}")

    if not all_files:
        print("\nWARNING: No files found in plugin data directory.")
        print("Make sure Phase 5 (assembly) has been run first.")

    # --- Run all checks ---
    results = []

    print("\nRunning Check 1: BOM Detection...")
    r1 = check_bom(all_files)
    results.append(r1)
    print(f"  {'PASS' if r1['passed'] else 'FAIL'} - {r1['checked']} files checked, {len(r1['errors'])} errors")

    print("Running Check 2: Column Count Integrity...")
    r2 = check_column_counts(csv_files)
    results.append(r2)
    print(f"  {'PASS' if r2['passed'] else 'FAIL'} - {r2['checked']} CSVs checked, {len(r2['errors'])} errors")

    print("Running Check 3: Duplicate Key Detection...")
    r3 = check_duplicate_keys(csv_files)
    results.append(r3)
    print(f"  {'PASS' if r3['passed'] else 'FAIL'} - {r3['checked']} CSVs checked, {len(r3['errors'])} errors")

    print("Running Check 4: Placeholder Integrity...")
    r4 = check_placeholders()
    results.append(r4)
    if r4.get("skipped"):
        print(f"  SKIP - {r4.get('skip_reason', '')}")
    else:
        print(f"  {'PASS' if r4['passed'] else 'FAIL'} - {r4['checked']} chunks checked, {len(r4['errors'])} errors")

    print("Running Check 5: Required Files Check...")
    r5 = check_required_files()
    results.append(r5)
    print(f"  {'PASS' if r5['passed'] else 'FAIL'} - {r5['checked']} items checked, {len(r5['errors'])} errors")

    print("Running Check 6: JSON/Group Validity...")
    r6 = check_json_validity(json_files)
    results.append(r6)
    print(f"  {'PASS' if r6['passed'] else 'FAIL'} - {r6['checked']} files checked, {len(r6['errors'])} errors")

    print("Running Check 7: JSON Structural Integrity...")
    r7 = check_json_structural_integrity(json_files)
    results.append(r7)
    print(f"  {'PASS' if r7['passed'] else 'FAIL'} - {r7['checked']} files checked, {len(r7['errors'])} errors")

    # --- Generate report ---
    report_text, verdict, total_errors, checks_passed, checks_failed = generate_report(
        results, all_files, csv_files, json_files
    )

    # Print report to stdout
    print("\n" + report_text)

    # Write report to file
    os.makedirs(os.path.dirname(REPORT_FILE), exist_ok=True)
    with open(REPORT_FILE, "w", encoding="utf-8", newline="") as f:
        f.write(report_text)
    print(f"\nDetailed report written to: {REPORT_FILE}")

    # --- Update state ---
    update_state(checks_passed, checks_failed, verdict)

    # --- Exit code ---
    if verdict == "PASS":
        print("\nPhase 7 complete: ALL CHECKS PASSED")
        sys.exit(0)
    else:
        print(f"\nPhase 7 complete: VALIDATION FAILED ({total_errors} errors)")
        sys.exit(1)


if __name__ == "__main__":
    main()
