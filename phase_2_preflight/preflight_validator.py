#!/usr/bin/env python3
"""
Phase 2 - Pre-flight Validator
================================
Validates extracted chunks from Phase 1 before LLM translation.
Checks schema integrity, catalogs placeholders, maps glossary coverage,
estimates token counts, and filters empty text.

Usage:
    python phase_2_preflight/preflight_validator.py
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
CHUNKS_DIR = PROJECT_ROOT / "data" / "chunks"
INPUT_PATH = CHUNKS_DIR / "phase1_extracted.json"
VALIDATED_PATH = CHUNKS_DIR / "phase2_validated.json"
REJECTED_PATH = CHUNKS_DIR / "phase2_rejected.json"
GLOSSARY_PATH = PROJECT_ROOT / "localization_tracking" / "master_glossary.csv"
STATE_PATH = PROJECT_ROOT / "core" / "state.json"

# Token estimation safety multiplier
# Application text is English; 1 token ~ 4 chars is standard,
# but we use 1.5x character count as a conservative estimate for
# mixed English/technical text that may expand in Japanese.
TOKEN_SAFETY_MULTIPLIER = 1.5
TOKEN_LIMIT = 4000

# Regex patterns for placeholder detection
# Matches: $var, $varName, $onOrAt, ${var}, %s, %d, %f, %.2f, %1$s, {var}, {{var}}
PLACEHOLDER_PATTERNS = [
    (r'\$\{[^}]+\}',        'dollar_brace'),    # ${variable}
    (r'\$[a-zA-Z_]\w*',     'dollar_var'),       # $variable
    (r'%\d*\$?[sdfu]',      'printf_positional'),# %1$s, %s, %d, etc.
    (r'%\.?\d*[sdfeEgG]',   'printf_format'),    # %.2f, %s, %d, etc.
    (r'\{\{[^}]+\}\}',      'double_brace'),     # {{variable}}
    (r'\{[a-zA-Z_]\w*\}',   'single_brace'),     # {variable}
]

# Compile all patterns into one combined list
PLACEHOLDER_REGEXES = [(re.compile(pat), label) for pat, label in PLACEHOLDER_PATTERNS]


# =============================================================================
# Helpers
# =============================================================================

def scrub_bom(raw_bytes: bytes) -> bytes:
    """Strip UTF-8 BOM if present."""
    if raw_bytes.startswith(b'\xef\xbb\xbf'):
        return raw_bytes[3:]
    return raw_bytes


def load_glossary() -> list[dict]:
    """
    Load the master glossary CSV.
    Returns list of dicts with keys: English Source, Japanese Translation, Type,
    Context & Localization Nuance, Status.
    """
    if not GLOSSARY_PATH.exists():
        print(f"[WARNING] Glossary file not found: {GLOSSARY_PATH}")
        return []

    raw = GLOSSARY_PATH.read_bytes()
    raw = scrub_bom(raw)
    text = raw.decode('utf-8')
    reader = csv.DictReader(io.StringIO(text))
    entries = []
    for row in reader:
        english = row.get("English Source", "").strip()
        if english:
            entries.append(row)
    return entries


def load_chunks() -> list[dict]:
    """Load Phase 1 extracted chunks."""
    if not INPUT_PATH.exists():
        print(f"[ERROR] Phase 1 output not found: {INPUT_PATH}")
        print("       Run phase_1_extraction/extraction_engine.py first.")
        sys.exit(1)

    raw = INPUT_PATH.read_bytes()
    raw = scrub_bom(raw)
    return json.loads(raw.decode('utf-8'))


def find_placeholders(text: str) -> list[dict]:
    """
    Find all placeholders in a text string.
    Returns a list of dicts: {placeholder, type, position}
    """
    found = []
    seen_spans = set()  # Avoid duplicate matches from overlapping patterns

    for regex, label in PLACEHOLDER_REGEXES:
        for match in regex.finditer(text):
            span = (match.start(), match.end())
            if span not in seen_spans:
                seen_spans.add(span)
                found.append({
                    "placeholder": match.group(),
                    "type": label,
                    "position": match.start(),
                })

    # Sort by position for consistent ordering
    found.sort(key=lambda x: x["position"])
    return found


def find_glossary_hits(text: str, glossary: list[dict]) -> list[dict]:
    """
    Check if any glossary English terms appear in the source text.
    Returns list of matching glossary entries (simplified).
    Uses case-insensitive matching. Matches whole words where feasible
    but also handles multi-word terms.
    """
    hits = []
    text_lower = text.lower()

    for entry in glossary:
        english = entry.get("English Source", "").strip()
        if not english:
            continue

        # Case-insensitive substring check first (fast filter)
        if english.lower() not in text_lower:
            continue

        # Confirmed match -- record it
        hits.append({
            "english": english,
            "japanese": entry.get("Japanese Translation", "").strip(),
            "type": entry.get("Type", "").strip(),
            "status": entry.get("Status", "").strip(),
        })

    return hits


def estimate_tokens(text: str) -> int:
    """
    Conservative token count estimate.
    Uses character count * multiplier as a rough upper bound.
    """
    return int(len(text) * TOKEN_SAFETY_MULTIPLIER)


# =============================================================================
# Validation pipeline
# =============================================================================

def validate_chunk(chunk: dict, glossary: list[dict]) -> tuple[dict | None, dict | None]:
    """
    Validate a single chunk. Returns (validated_chunk, None) if OK,
    or (None, rejected_chunk) if the chunk fails validation.
    
    Checks:
    1. Schema: required fields present and non-empty
    2. Empty text: skip whitespace-only source_text
    3. Token estimate: flag if > TOKEN_LIMIT
    4. Placeholder catalog: find and store placeholders
    5. Glossary coverage: find matching glossary terms
    """
    rejection_reasons = []

    # ---- 1. Schema check ----
    required_fields = ["source_text", "chunk_type", "context_tag", "source_file"]
    for field in required_fields:
        value = chunk.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            rejection_reasons.append(f"Missing or empty required field: {field}")

    # If schema fails, reject immediately
    if rejection_reasons:
        rejected = dict(chunk)
        rejected["rejection_reasons"] = rejection_reasons
        return None, rejected

    source_text = chunk["source_text"]

    # ---- 2. Empty text filter ----
    if not source_text.strip():
        rejected = dict(chunk)
        rejected["rejection_reasons"] = ["source_text is empty or whitespace-only"]
        return None, rejected

    # ---- 3. Token estimate ----
    token_est = estimate_tokens(source_text)
    if token_est > TOKEN_LIMIT:
        rejection_reasons.append(
            f"Token estimate ({token_est}) exceeds limit ({TOKEN_LIMIT})"
        )

    # Token oversize is a warning, not a hard reject in most cases.
    # But we flag it. We still allow it through with a flag.
    # Only reject if the text is absurdly large (>10x limit).
    if token_est > TOKEN_LIMIT * 10:
        rejected = dict(chunk)
        rejected["rejection_reasons"] = [
            f"Token estimate ({token_est}) vastly exceeds limit ({TOKEN_LIMIT})"
        ]
        return None, rejected

    # ---- 4. Placeholder catalog ----
    placeholders = find_placeholders(source_text)

    # ---- 5. Glossary coverage ----
    glossary_hits = find_glossary_hits(source_text, glossary)

    # Build validated chunk
    validated = dict(chunk)
    validated["placeholders"] = placeholders
    validated["glossary_hits"] = glossary_hits
    validated["token_estimate"] = token_est

    if token_est > TOKEN_LIMIT:
        validated["token_warning"] = True

    return validated, None


def update_state(validated_count: int, rejected_count: int):
    """Update state.json to mark phase 2 as complete."""
    if STATE_PATH.exists():
        raw = STATE_PATH.read_bytes()
        raw = scrub_bom(raw)
        state = json.loads(raw.decode('utf-8'))
    else:
        state = {}

    state["current_phase"] = 2
    state.setdefault("phases", {})
    state["phases"]["2_preflight"] = {
        "status": "complete",
        "chunks_validated": validated_count,
        "chunks_rejected": rejected_count,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }

    with open(STATE_PATH, 'w', encoding='utf-8', newline='') as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def print_summary(validated: list, rejected: list, glossary: list):
    """Print a formatted summary table."""
    print("\n" + "=" * 78)
    print("  PHASE 2 PRE-FLIGHT VALIDATION SUMMARY")
    print("=" * 78)

    total = len(validated) + len(rejected)
    print(f"\n  Input chunks:     {total:>8}")
    print(f"  Validated:        {len(validated):>8}")
    print(f"  Rejected:         {len(rejected):>8}")

    # Validated by chunk_type
    type_counts = {}
    for chunk in validated:
        ct = chunk["chunk_type"]
        type_counts[ct] = type_counts.get(ct, 0) + 1

    print(f"\n  {'Validated by Type':<25} {'Count':>8}")
    print("  " + "-" * 35)
    for ct in sorted(type_counts.keys()):
        print(f"  {ct:<25} {type_counts[ct]:>8}")

    # Placeholder stats
    chunks_with_placeholders = sum(1 for c in validated if c.get("placeholders"))
    total_placeholders = sum(len(c.get("placeholders", [])) for c in validated)
    print(f"\n  Chunks with placeholders:  {chunks_with_placeholders}")
    print(f"  Total placeholders found:  {total_placeholders}")

    # Token warnings
    token_warnings = sum(1 for c in validated if c.get("token_warning"))
    if token_warnings:
        print(f"  [!] Chunks over token limit: {token_warnings}")

    # Glossary coverage
    chunks_with_glossary = sum(1 for c in validated if c.get("glossary_hits"))
    unique_glossary_hits = set()
    for c in validated:
        for hit in c.get("glossary_hits", []):
            unique_glossary_hits.add(hit["english"])
    print(f"\n  Glossary terms loaded:      {len(glossary)}")
    print(f"  Chunks with glossary hits:  {chunks_with_glossary}")
    print(f"  Unique glossary terms hit:  {len(unique_glossary_hits)}")

    # Rejection reasons breakdown
    if rejected:
        reason_counts = {}
        for chunk in rejected:
            for reason in chunk.get("rejection_reasons", ["unknown"]):
                # Normalize reason for counting
                key = reason.split(":")[0].strip() if ":" in reason else reason
                reason_counts[key] = reason_counts.get(key, 0) + 1

        print(f"\n  {'Rejection Reason':<45} {'Count':>8}")
        print("  " + "-" * 55)
        for reason in sorted(reason_counts.keys()):
            print(f"  {reason:<45} {reason_counts[reason]:>8}")

    print("\n" + "=" * 78)


# =============================================================================
# Main
# =============================================================================

def main():
    print("Phase 2 - Pre-flight Validator")
    print(f"Project root: {PROJECT_ROOT}")
    print()

    # Load inputs
    chunks = load_chunks()
    print(f"Loaded {len(chunks)} chunks from Phase 1 output")

    glossary = load_glossary()
    print(f"Loaded {len(glossary)} glossary entries")
    print()

    validated = []
    rejected = []

    for i, chunk in enumerate(chunks):
        valid_chunk, reject_chunk = validate_chunk(chunk, glossary)
        if valid_chunk is not None:
            validated.append(valid_chunk)
        if reject_chunk is not None:
            rejected.append(reject_chunk)

        # Progress indicator every 500 chunks
        if (i + 1) % 500 == 0:
            print(f"  Processed {i + 1}/{len(chunks)} chunks...")

    print(f"  Processed {len(chunks)}/{len(chunks)} chunks... done")

    # Write outputs
    CHUNKS_DIR.mkdir(parents=True, exist_ok=True)

    with open(VALIDATED_PATH, 'w', encoding='utf-8', newline='') as f:
        json.dump(validated, f, indent=2, ensure_ascii=False)
    print(f"\nWrote {len(validated)} validated chunks to {VALIDATED_PATH}")

    with open(REJECTED_PATH, 'w', encoding='utf-8', newline='') as f:
        json.dump(rejected, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(rejected)} rejected chunks to {REJECTED_PATH}")

    # Update state
    update_state(len(validated), len(rejected))
    print(f"Updated state.json (phase 2 = complete)")

    # Print summary
    print_summary(validated, rejected, glossary)


if __name__ == "__main__":
    main()
