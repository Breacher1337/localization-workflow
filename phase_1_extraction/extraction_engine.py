import sys
import os
import config
#!/usr/bin/env python3
"""
Phase 1 - Extraction Engine
============================
Reads the localization masterlist, extracts all translatable text from
Application application source files (CSV, JSON, .group), tags each chunk with
context metadata, and outputs chunked JSON for the translation pipeline.

Usage:
    python phase_1_extraction/extraction_engine.py
    (Run from project root: .)
"""

import sys
import io
import os
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

# -- Windows console UTF-8 safety --
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# =============================================================================
# Configuration
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
APPLICATION_DATA_ROOT = Path(config.APPLICATION_CORE_DIR)
MASTERLIST_PATH = PROJECT_ROOT / "localization_masterlist.csv"
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
STATE_PATH = PROJECT_ROOT / "core" / "state.json"
OUTPUT_PATH = CHUNKS_DIR / "phase1_extracted.json"

# ---- Per-file translatable column definitions ----
# Maps a filename pattern to (translatable_columns, id_column, context_tag, chunk_type)
# id_column: which column to use as the row key for reassembly
# context_tag: semantic label for the chunk
# chunk_type: "UI", "Dialogue", or "Lore"
CSV_COLUMN_MAP = {
    "campaign/abilities.csv": {
        "columns": ["name", "desc"],
        "id_col": "id",
        "context_tag": "ability_name",
        "chunk_type": "UI",
    },
    "campaign/compluginities.csv": {
        "columns": ["name", "desc"],
        "id_col": "id",
        "context_tag": "compluginity",
        "chunk_type": "UI",
    },
    "campaign/industries.csv": {
        "columns": ["name", "desc"],
        "id_col": "id",
        "context_tag": "industry",
        "chunk_type": "UI",
    },
    "campaign/market_conditions.csv": {
        "columns": ["name", "desc"],
        "id_col": "id",
        "context_tag": "market_condition",
        "chunk_type": "Lore",
    },
    "campaign/procgen/name_gen_data.csv": {
        "columns": ["name"],
        "id_col": "name",  # composite key: name+tags
        "context_tag": "procedural_name",
        "chunk_type": "Lore",
    },
    "campaign/reports.csv": {
        "columns": ["subject", "summary", "assessment"],
        "id_col": "event_type",
        "context_tag": "intel_report",
        "chunk_type": "Lore",
    },
    "campaign/rules.csv": {
        "columns": ["text", "options"],
        "id_col": "id",
        "context_tag": "dialogue_rule",
        "chunk_type": "Dialogue",
    },
    "campaign/special_items.csv": {
        "columns": ["name", "desc"],
        "id_col": "id",
        "context_tag": "special_item",
        "chunk_type": "UI",
    },
    "campaign/submarkets.csv": {
        "columns": ["name", "desc"],
        "id_col": "id",
        "context_tag": "submarket",
        "chunk_type": "UI",
    },
    "characters/person_names.csv": {
        "columns": ["name"],
        "id_col": "name",
        "context_tag": "person_name",
        "chunk_type": "Lore",
    },
    "characters/personalities.csv": {
        "columns": ["name", "desc"],
        "id_col": "id",
        "context_tag": "personality",
        "chunk_type": "UI",
    },
    "characters/skills/aptitude_data.csv": {
        "columns": ["name", "description"],
        "id_col": "id",
        "context_tag": "aptitude",
        "chunk_type": "UI",
    },
    "characters/skills/skill_data.csv": {
        "columns": ["name", "description", "author"],
        "id_col": "id",
        "context_tag": "skill",
        "chunk_type": "UI",
    },
    "hullplugins/hull_plugins.csv": {
        "columns": ["name", "desc", "short", "sPluginDesc"],
        "id_col": "id",
        "context_tag": "hull_plugin",
        "chunk_type": "UI",
    },
    "hulls/ship_data.csv": {
        "columns": ["name", "designation"],
        "id_col": "id",
        "context_tag": "ship",
        "chunk_type": "UI",
    },
    "shipsystems/ship_systems.csv": {
        "columns": ["name"],
        "id_col": "id",
        "context_tag": "ship_system",
        "chunk_type": "UI",
    },
    "strings/descriptions.csv": {
        "columns": ["text1", "text2", "text3", "text4", "text5"],
        "id_col": "id",
        "context_tag": "description",
        "chunk_type": "Lore",
    },
    "weapons/weapon_data.csv": {
        "columns": ["name", "primaryRoleStr", "customPrimary", "customPrimaryHL",
                     "customAncillary", "customAncillaryHL"],
        "id_col": "id",
        "context_tag": "weapon",
        "chunk_type": "UI",
    },
}

# ---- Group file translatable keys ----
# These are the keys whose string values should be extracted from .group files.
# Nested structures under "ranks" and "fleetTypeNames" are handled specially.
FACTION_TRANSLATABLE_KEYS = [
    "displayName",
    "displayNameWithArticle",
    "displayNameLong",
    "displayNameLongWithArticle",
    "displayNameIsOrAre",
    "personNamePrefix",
    "personNamePrefixAOrAn",
]


# =============================================================================
# Helpers
# =============================================================================

def normalize_path(raw_path: str) -> str:
    """Convert backslash Windows paths to forward-slash for consistency."""
    return raw_path.replace("\\", "/")


def scrub_bom(raw_bytes: bytes) -> bytes:
    """Strip UTF-8 BOM if present."""
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        return raw_bytes[3:]
    return raw_bytes


def read_csv_file(filepath: Path) -> list[dict]:
    """
    Read a Application CSV file, handling BOM, comment rows (starting with #),
    and empty separator rows.  Returns a list of dicts keyed by header.
    """
    raw = filepath.read_bytes()
    raw = scrub_bom(raw)
    text = raw.decode('utf-8')

    # Parse with csv.reader first to properly handle quoted newlines (e.g. in script column)
    reader = csv.reader(io.StringIO(text))
    rows = []
    for row in reader:
        if not row:
            continue
        # Filter out comment rows that start with #
        if row[0].lstrip().startswith('#'):
            continue
        rows.append(row)

    if not rows:
        return []

    header = rows[0]
    dict_rows = []
    for row in rows[1:]:
        dict_rows.append(dict(zip(header, row)))
    
    return dict_rows


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
    bare_key_re = re.compile(
        r'^(\s*)'           # group 1: leading whitespace
        r'([a-zA-Z_][a-zA-Z0-9_]*)'  # group 2: bare key
        r'(\s*:\s*)'        # group 3: colon with optional whitespace
    )

    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#") or stripped.startswith('"'):
            result.append(line)
            continue
        if stripped[0] in "]}),":
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


def parse_json_with_comments(text: str) -> object:
    """
    Parse Application's lenient JSON (with comments, trailing commas,
    unquoted keys, float suffixes). Uses a multi-pass approach.
    """
    # Step 1: Remove comments
    text = strip_json_comments(text)

    # Step 2: Remove trailing commas before } or ]
    text = re.sub(r",\s*([}\]])", r"\1", text)

    # Step 3: Strip trailing commas and whitespace from the end of the file
    text = text.strip()
    if text.endswith(','):
        text = text[:-1].strip()

    # Step 4: Remove float suffixes (e.g. 1f -> 1, 0.5f -> 0.5)
    text = re.sub(r'\b(\d+\.?\d*)f\b', r'\1', text)

    # Step 5: Try standard JSON first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Step 6: Try quoting bare keys (HJSON-style)
    quoted = quote_bare_keys(text)
    return json.loads(quoted)


def extract_json_strings(obj, path_prefix="", results=None):
    """
    Recursively extract all string values from a JSON object.
    Returns list of (json_path, string_value) tuples.
    """
    if results is None:
        results = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            current_path = f"{path_prefix}['{key}']" if path_prefix else f"['{key}']"
            extract_json_strings(value, current_path, results)
    elif isinstance(obj, list):
        for idx, value in enumerate(obj):
            current_path = f"{path_prefix}[{idx}]"
            extract_json_strings(value, current_path, results)
    elif isinstance(obj, str):
        results.append((path_prefix, obj))

    return results


def classify_json_context(file_path_norm: str, json_path: str) -> tuple[str, str]:
    """
    Determine chunk_type and context_tag for a JSON-extracted string
    based on file path and JSON key path.
    """
    basename = file_path_norm.split('/')[-1].lower()

    if basename == "strings.json":
        return ("UI", "ui_string")
    elif basename == "tips.json":
        return ("UI", "combat_tip")
    elif basename == "tooltips.json":
        return ("UI", "tooltip")
    elif basename == "ship_names.json":
        return ("Lore", "ship_name")
    elif basename == "default_fleet_type_names.json":
        return ("UI", "fleet_type_name")
    else:
        return ("Lore", "json_text")


def classify_group_context(json_path: str) -> tuple[str, str]:
    """Classify group file chunks."""
    path_lower = json_path.lower()
    if "displayname" in path_lower:
        return ("Lore", "group_display_name")
    elif "ranks" in path_lower or "posts" in path_lower:
        return ("UI", "group_rank")
    elif "fleettypenames" in path_lower:
        return ("UI", "fleet_type_name")
    elif "personname" in path_lower:
        return ("Lore", "group_person_prefix")
    else:
        return ("Lore", "group_text")


# =============================================================================
# Extraction routines
# =============================================================================

def extract_csv_file(source_path: Path, file_path_norm: str, config: dict) -> list[dict]:
    """Extract translatable columns from a CSV file."""
    chunks = []

    try:
        rows = read_csv_file(source_path)
    except Exception as e:
        print(f"  [WARNING] Failed to read CSV {source_path}: {e}")
        return chunks

    columns = config["columns"]
    id_col = config["id_col"]
    context_tag = config["context_tag"]
    chunk_type = config["chunk_type"]

    # Validate that expected columns exist in the file
    if not rows:
        return chunks
    available_cols = set(rows[0].keys())

    for row_idx, row in enumerate(rows):
        # Determine row key
        row_key = row.get(id_col, "").strip() if id_col else ""

        # For name_gen_data.csv, build composite key
        if file_path_norm.endswith("name_gen_data.csv"):
            name_val = row.get("name", "").strip()
            tags_val = row.get("tags", "").strip()
            row_key = f"{name_val}|{tags_val}"
        # For descriptions.csv, build composite key (id + type)
        elif file_path_norm.endswith("descriptions.csv"):
            id_val = row.get("id", "").strip()
            type_val = row.get("type", "").strip()
            row_key = f"{id_val}|{type_val}"
        # For reports.csv, build composite key (event_type + event_stage)
        elif file_path_norm.endswith("reports.csv"):
            type_val = row.get("event_type", "").strip()
            stage_val = row.get("event_stage", "").strip()
            row_key = f"{type_val}|{stage_val}"

        # Skip rows with empty/missing ID (separator rows)
        if not row_key:
            continue

        for col in columns:
            if col not in available_cols:
                continue
            text = row.get(col, "")
            if text is None:
                continue
            text = text.strip()
            if not text:
                continue

            chunk = {
                "source_file": file_path_norm,
                "chunk_type": chunk_type,
                "context_tag": context_tag,
                "source_text": text,
                "row_key": row_key,
                "column": col,
            }
            chunks.append(chunk)

    return chunks


def extract_json_file(source_path: Path, file_path_norm: str) -> list[dict]:
    """Extract all string values from a JSON file."""
    chunks = []

    try:
        raw = source_path.read_bytes()
        raw = scrub_bom(raw)
        text = raw.decode('utf-8')
        data = parse_json_with_comments(text)
    except Exception as e:
        print(f"  [WARNING] Failed to parse JSON {source_path}: {e}")
        return chunks

    strings = extract_json_strings(data)

    for json_path, string_value in strings:
        text = string_value.strip()
        if not text:
            continue

        chunk_type, context_tag = classify_json_context(file_path_norm, json_path)

        chunk = {
            "source_file": file_path_norm,
            "chunk_type": chunk_type,
            "context_tag": context_tag,
            "source_text": text,
            "row_key": json_path,
            "column": json_path,
        }
        chunks.append(chunk)

    return chunks


def extract_group_file(source_path: Path, file_path_norm: str) -> list[dict]:
    """
    Extract translatable text from a .group file.
    Targets specific keys: displayName variants, ranks, posts,
    personNamePrefix, fleetTypeNames, etc.
    """
    chunks = []

    try:
        raw = source_path.read_bytes()
        raw = scrub_bom(raw)
        text = raw.decode('utf-8')
        data = parse_json_with_comments(text)
    except Exception as e:
        print(f"  [WARNING] Failed to parse group file {source_path}: {e}")
        return chunks

    group_id = data.get("id", source_path.stem)

    # 1. Extract top-level translatable string keys
    for key in FACTION_TRANSLATABLE_KEYS:
        if key in data and isinstance(data[key], str):
            text = data[key].strip()
            if not text:
                continue
            chunk_type, context_tag = classify_group_context(key)
            chunk = {
                "source_file": file_path_norm,
                "chunk_type": chunk_type,
                "context_tag": context_tag,
                "source_text": text,
                "row_key": f"{group_id}.{key}",
                "column": key,
            }
            chunks.append(chunk)

    # 2. Extract ranks -> ranks -> {role}: {name: "..."}
    ranks_section = data.get("ranks", {})
    if isinstance(ranks_section, dict):
        for section_key in ["ranks", "posts"]:
            section = ranks_section.get(section_key, {})
            if isinstance(section, dict):
                for role_id, role_data in section.items():
                    if isinstance(role_data, dict) and "name" in role_data:
                        text = role_data["name"].strip()
                        if not text:
                            continue
                        json_path = f"ranks.{section_key}.{role_id}.name"
                        chunk_type, context_tag = classify_group_context(json_path)
                        chunk = {
                            "source_file": file_path_norm,
                            "chunk_type": chunk_type,
                            "context_tag": context_tag,
                            "source_text": text,
                            "row_key": f"{group_id}.{json_path}",
                            "column": json_path,
                        }
                        chunks.append(chunk)

    # 3. Extract fleetTypeNames (dict of key: display_name)
    fleet_names = data.get("fleetTypeNames", {})
    if isinstance(fleet_names, dict):
        for fleet_key, fleet_name in fleet_names.items():
            if isinstance(fleet_name, str):
                text = fleet_name.strip()
                if not text:
                    continue
                json_path = f"fleetTypeNames.{fleet_key}"
                chunk_type, context_tag = classify_group_context(json_path)
                chunk = {
                    "source_file": file_path_norm,
                    "chunk_type": chunk_type,
                    "context_tag": context_tag,
                    "source_text": text,
                    "row_key": f"{group_id}.{json_path}",
                    "column": json_path,
                }
                chunks.append(chunk)

    return chunks


# =============================================================================
# Main pipeline
# =============================================================================

def load_masterlist() -> list[dict]:
    """Load the localization masterlist CSV."""
    if not MASTERLIST_PATH.exists():
        print(f"[ERROR] Masterlist not found: {MASTERLIST_PATH}")
        sys.exit(1)

    raw = MASTERLIST_PATH.read_bytes()
    raw = scrub_bom(raw)
    text = raw.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def update_state(chunk_count: int):
    """Update state.json to mark phase 1 as complete."""
    if STATE_PATH.exists():
        raw = STATE_PATH.read_bytes()
        raw = scrub_bom(raw)
        state = json.loads(raw.decode('utf-8'))
    else:
        state = {}

    state["current_phase"] = 1
    state.setdefault("phases", {})
    state["phases"]["1_extraction"] = {
        "status": "complete",
        "chunks_extracted": chunk_count,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(STATE_PATH, 'w', encoding='utf-8', newline='') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def print_summary(file_stats: dict, all_chunks: list):
    """Print a formatted summary table."""
    print("\n" + "=" * 78)
    print("  PHASE 1 EXTRACTION SUMMARY")
    print("=" * 78)

    # Per-file table
    print(f"\n  {'File':<48} {'Chunks':>8}  {'Type':<10}")
    print("  " + "-" * 74)
    for fpath in sorted(file_stats.keys()):
        info = file_stats[fpath]
        print(f"  {fpath:<48} {info['count']:>8}  {info['file_type']:<10}")

    # Totals by chunk_type
    type_counts = {}
    for chunk in all_chunks:
        ct = chunk["chunk_type"]
        type_counts[ct] = type_counts.get(ct, 0) + 1

    print(f"\n  {'Chunk Type':<20} {'Count':>8}")
    print("  " + "-" * 30)
    for ct in sorted(type_counts.keys()):
        print(f"  {ct:<20} {type_counts[ct]:>8}")

    # Context tag breakdown
    tag_counts = {}
    for chunk in all_chunks:
        tag = chunk["context_tag"]
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print(f"\n  {'Context Tag':<30} {'Count':>8}")
    print("  " + "-" * 40)
    for tag in sorted(tag_counts.keys()):
        print(f"  {tag:<30} {tag_counts[tag]:>8}")

    print(f"\n  Total files processed: {len(file_stats)}")
    print(f"  Total chunks extracted: {len(all_chunks)}")
    print("=" * 78)


def main():
    print("Phase 1 - Extraction Engine")
    print(f"Application data root: {APPLICATION_DATA_ROOT}")
    print(f"Project root:   {PROJECT_ROOT}")
    print()

    # Ensure output directory exists
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    # Load masterlist
    masterlist = load_masterlist()
    print(f"Loaded {len(masterlist)} entries from masterlist")

    all_chunks = []
    file_stats = {}

    for entry in masterlist:
        raw_path = entry.get("File Path", "").strip()
        file_type = entry.get("Type", "").strip().upper()

        if not raw_path:
            continue

        # Normalize to forward slashes
        file_path_norm = normalize_path(raw_path)

        # Resolve full source path
        source_path = APPLICATION_DATA_ROOT / file_path_norm
        if not source_path.exists():
            print(f"  [SKIP] Source file not found: {source_path}")
            continue

        print(f"  Processing: {file_path_norm} ({file_type})")

        # Dispatch extraction by file type
        if file_type == "CSV":
            # Find matching config
            config_key = file_path_norm
            config = CSV_COLUMN_MAP.get(config_key)
            if not config:
                print(f"    [WARNING] No column mapping for {file_path_norm}, skipping")
                continue
            chunks = extract_csv_file(source_path, file_path_norm, config)

        elif file_type == "JSON":
            # Check if it's a .group file
            if source_path.suffix == ".group":
                chunks = extract_group_file(source_path, file_path_norm)
            else:
                chunks = extract_json_file(source_path, file_path_norm)
        else:
            print(f"    [WARNING] Unknown file type '{file_type}', skipping")
            continue

        all_chunks.extend(chunks)
        file_stats[file_path_norm] = {
            "count": len(chunks),
            "file_type": file_type if source_path.suffix != ".group" else "FACTION",
        }

    # Write output
    with open(OUTPUT_PATH, 'w', encoding='utf-8', newline='') as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\nWrote {len(all_chunks)} chunks to {OUTPUT_PATH}")

    # Update state
    update_state(len(all_chunks))
    print(f"Updated state.json (phase 1 = complete)")

    # Print summary
    print_summary(file_stats, all_chunks)


if __name__ == "__main__":
    main()
