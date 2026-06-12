"""
Scaffold the Agentic Localization Pipeline workspace.
Creates all directories and files defined in architecture.txt.
"""
import os
import json

ROOT = r"."

# === Directories to create ===
dirs = [
    "core",
    "phase_0_glossary",
    "phase_1_extraction",
    "phase_2_preflight",
    "phase_3_translation",
    "phase_4_critic",
    "phase_5_assembly",
    "phase_6_human_review",
    "phase_7_engine_validation",
]

for d in dirs:
    path = os.path.join(ROOT, d)
    os.makedirs(path, exist_ok=True)
    print(f"  DIR: {d}/")

print()

# === Files to create (only if they don't already exist) ===
# We'll track what we create
created = []
skipped = []

def create_file(relpath, content):
    path = os.path.join(ROOT, relpath)
    if os.path.exists(path):
        skipped.append(relpath)
        return
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    created.append(relpath)

# ============================================================
# CORE FILES
# ============================================================

# state.json placeholder
create_file("core/state.json", json.dumps({
    "project": "application-jp",
    "version": "1.0",
    "current_phase": 0,
    "current_chunk": None,
    "glossary_locked": False,
    "phases": {
        "0_glossary": {"status": "pending", "glossary_version": None},
        "1_extraction": {"status": "pending", "chunks_extracted": 0},
        "2_preflight": {"status": "pending", "chunks_validated": 0, "chunks_rejected": 0},
        "3_translation": {"status": "pending", "chunks_translated": 0, "chunks_pending": 0},
        "4_critic": {"status": "pending", "chunks_approved": 0, "chunks_revised": 0},
        "5_assembly": {"status": "pending", "files_merged": 0},
        "6_human_review": {"status": "pending", "corrections": 0},
        "7_validation": {"status": "pending", "checks_passed": 0, "checks_failed": 0}
    },
    "critic_feedback": {
        "approved": None,
        "reason": None,
        "revised_translation": None
    }
}, indent=2, ensure_ascii=False))

# orchestrator_agent.md
create_file("core/orchestrator_agent.md", """# Orchestrator Agent

## Role
The State Manager. You do not translate. You read `state.json` and route data to the appropriate tools or sub-agents.

## Behavior
1. Check `state.current_phase`.
2. If Phase 0: Route to `glossary_agent` for term extraction and proposal. Await human lock.
3. If Phase 1: Execute `extraction_engine.py` deterministically. Do NOT use an LLM.
4. If Phase 2: Execute `preflight_validator.py` deterministically. Gate all chunks.
5. If Phase 3 and `state.current_chunk.type == "UI"`: Route to `translator_subagent_ui`.
6. If Phase 3 and `state.current_chunk.type == "Dialogue"`: Route to `translator_subagent_dialogue`.
7. If Phase 4: Route to `critic_agent` for quality review.
8. If Phase 4 and `state.critic_feedback.approved == false`: Update `state.current_chunk.translation` with `state.critic_feedback.revised_translation` and advance to Phase 5. Do NOT loop back to Phase 3.
9. If Phase 5: Execute `merge_engine.py` and `deterministic_sanitizer.py` deterministically.
10. If Phase 6: Present sample to human. Record corrections in `corrections_log.json`.
11. If Phase 7: Execute `protocol_check.py` deterministically. Gate for production.

## State Flow
```
Phase 0 → Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7
  ↑                                         │
  └─── corrections_log (feedback loop) ─────┘
```

## Critical Rules
- **NEVER** use an LLM for Phases 1, 2, 5, or 7. These are deterministic.
- **NEVER** loop Phase 4 back to Phase 3. The Critic rewrites inline.
- **ALWAYS** read `state.json` before any action.
- **ALWAYS** update `state.json` after any phase transition.
""")

# AGENTS.md — already exists, skip (will be handled by skipped list)

# ============================================================
# PHASE 0: GLOSSARY
# ============================================================

create_file("phase_0_glossary/glossary_agent.md", """# Glossary Agent

## Role
Terminology Extraction and Mapping.

## System Prompt
Analyze the batch of source text. Identify recurring proper nouns, UI elements, and key verbs. Propose English to Japanese mappings. You must provide the proposed Kanji/Katakana, the target Part of Speech (noun, verb_suru), and a semantic context tag to prevent polysemy collisions later in the pipeline.

## Input
A batch of English source text strings from the application files.

## Output Schema
```json
[
  {
    "term_en": "string",
    "translations": [
      {
        "ja": "string",
        "context": "string (e.g., 'group_name', 'ui_button', 'lore_noun')",
        "pos": "string (e.g., 'noun', 'verb_suru', 'adjective')"
      }
    ]
  }
]
```

## Constraints
- Proper nouns (group names, character names, star systems) MUST use phonetic Katakana transliteration, NOT semantic translation.
- UI buttons MUST be concise (≤6 characters ideal).
- Context tags MUST be populated for every entry to prevent downstream Kanji polysemy errors.
- The output is a PROPOSAL. It becomes authoritative only after human lock into `locked_glossary_v1.json`.

## Reference
The existing locked glossary is at `../localization_tracking/master_glossary.csv` (200 entries, 5 columns: English Source, Japanese Translation, Type, Context & Localization Nuance, Status).
""")

create_file("phase_0_glossary/locked_glossary_v1.json", json.dumps({
    "_meta": {
        "version": "1.0",
        "locked_by": "human_arbiter",
        "locked_at": None,
        "source": "localization_tracking/master_glossary.csv",
        "entry_count": 0
    },
    "entries": []
}, indent=2, ensure_ascii=False))

# ============================================================
# PHASE 1: EXTRACTION
# ============================================================

create_file("phase_1_extraction/extraction_engine.py", '''"""
Phase 1: Source Extraction Engine (DETERMINISTIC — NO LLM)

Strips logic columns from application CSVs/JSONs, chunks translatable text,
and tags each chunk by context (UI vs. Dialogue vs. Lore).

Input:  Raw application data files (CSV, JSON, .group)
Output: Chunked JSON files tagged with context type, ready for Phase 2.
"""
# TODO: Implement extraction logic
# - Read source CSV/JSON files
# - Strip non-translatable columns (IDs, numeric values, logic scripts)
# - Tag each chunk with context_type: "UI", "Dialogue", or "Lore"
# - Output chunked JSON to /data/chunks/
# - Update state.json with chunk count
''')

# ============================================================
# PHASE 2: PREFLIGHT
# ============================================================

create_file("phase_2_preflight/preflight_validator.py", '''"""
Phase 2: Pre-Flight Validator (DETERMINISTIC — NO LLM)

Hard gate before LLM translation. Validates extracted chunks for:
- Schema correctness (all required fields present)
- Glossary coverage (all glossary terms in chunk have mappings)
- Placeholder integrity (variables, HTML tags preserved)
- Chunk size limits (prevent token overflow)

Input:  Chunked JSON files from Phase 1
Output: Validated chunks passed to Phase 3, rejected chunks logged
"""
# TODO: Implement validation logic
# - Load locked_glossary_v1.json
# - For each chunk:
#   - Validate schema (source_text, context_tag, chunk_type present)
#   - Check all English proper nouns against glossary
#   - Verify placeholders ($var, %s, {var}) are catalogued
#   - Reject if chunk exceeds token limit
# - Update state.json with validated/rejected counts
''')

# ============================================================
# PHASE 3: TRANSLATION
# ============================================================

create_file("phase_3_translation/translator_subagent_ui.md", """# UI Translator Sub-Agent

## Role
Strict English to Japanese UI Localization.

## System Prompt
You are an expert software localizer. Translate the provided English UI string to Japanese.
- You MUST reference the `locked_glossary_v1.json`. Match the `context` tag to ensure correct Kanji selection.
- Output MUST be concise standard Japanese (Desu/Masu form where applicable, or standard noun phrases for buttons).
- Preserve all variables exactly as written (e.g., `{UserName}`, `$group`, `%s`).

## Input Schema
```json
{
  "source_text": "string",
  "context_tag": "string",
  "glossary_reference": "object"
}
```

## Output Schema
```json
{
  "translation": "string"
}
```

## Constraints
- Maximum output length: source_text length × 1.5 (Japanese is more compact)
- Button labels: ≤6 characters
- Menu items: ≤12 characters
- Tooltips: natural length, formal register
- NEVER translate variable placeholders
- NEVER add explanatory text not in the source
""")

create_file("phase_3_translation/translator_subagent_dialogue.md", """# Dialogue Translator Sub-Agent

## Role
Creative English to Japanese Narrative Localization.

## System Prompt
You are an expert narrative translator. Translate the provided English dialogue into Japanese.
- You MUST apply the specified politeness register (`target_register`) and character voice (*Yakuwari-go*) defined in the payload.
- Ensure first-person pronouns (俺, 僕, 私, わたくし) and sentence-ending particles match the character profile.
- Do NOT overly sanitize the text. If the source is slang, use appropriate Japanese slang.

## Input Schema
```json
{
  "source_text": "string",
  "character_id": "string",
  "target_register": "string (e.g., 'formal_keigo', 'casual_tameguchi', 'military_formal', 'pirate_rough')",
  "glossary_reference": "object"
}
```

## Output Schema
```json
{
  "translation": "string"
}
```

## Register Guide (Yakuwari-go)
| Register | First-Person | Sentence Endings | Example Context |
|:---|:---|:---|:---|
| `formal_keigo` | 私(わたくし) | ～でございます, ～いたします | Tri-Tachyon executives, diplomats |
| `military_formal` | 私(わたし) | ～であります, ～であろう | Hegemony officers, Diktat commanders |
| `casual_tameguchi` | 俺, 僕 | ～だ, ～ぜ, ～よ | Pirates, Pathers, street contacts |
| `scholarly` | 私(わたし) | ～です, ～でしょう | Academy scholars, scientists |
| `religious` | 私(わたし) | ～でございます, ～なのです | Luddic Church clergy |
| `fanatical` | 我々, この身 | ～のだ!, ～べし! | Luddic Path zealots |

## Constraints
- Maintain the emotional weight and tone of the original
- Preserve all variables and formatting tags
- If a character's register is not specified, default to `military_formal`
""")

# ============================================================
# PHASE 4: CRITIC
# ============================================================

create_file("phase_4_critic/critic_agent.md", """# Critic Agent

## Role
Quality Assurance and Grammar Correction. The Lead Editor.

## System Prompt
You are the Lead Editor. Review the translated Japanese string against the English source.

### Checks (in order)
1. **Glossary Compliance:** Did it use the exact term from `locked_glossary`? Compare every glossary term that appears in the source against its translation.
2. **Register Check:** Does the translation match the `target_register`? Verify first-person pronouns, sentence endings, and formality level.
3. **Variable Integrity:** Are `{variables}`, `$variables`, and `%s` placeholders untouched and in correct positions?
4. **Naturalness:** Does the Japanese read naturally to a native speaker? Flag awkward phrasing.
5. **Completeness:** Is any meaning from the source text lost or added in translation?

### Critical Rule
If the translation fails ANY check, DO NOT send it back to the Translator. You must:
- Output `approved: false`
- Provide the reason for rejection
- Provide the fixed, corrected Japanese string in `revised_translation`

This prevents infinite translation↔critic loops that burn rate limits.

## Input Schema
```json
{
  "source_text": "string",
  "translation": "string",
  "target_register": "string",
  "chunk_type": "string"
}
```

## Output Schema
```json
{
  "approved": "boolean",
  "reason": "string",
  "revised_translation": "string | null"
}
```
""")

# ============================================================
# PHASE 5: ASSEMBLY
# ============================================================

create_file("phase_5_assembly/merge_engine.py", '''"""
Phase 5: Merge Engine (DETERMINISTIC — NO LLM)

Merges translated Japanese text back into the original application file
structures (CSV, JSON, .group), preserving all logic columns,
IDs, and non-translatable data.

Input:  Translated chunks from Phase 4 + original application file structures
Output: Complete localized application files ready for engine validation
"""
# TODO: Implement merge logic
# - Read original application files (structure template)
# - Read translated chunks
# - For each chunk, find the target cell/field and inject translation
# - Preserve: column order, row order, non-translatable columns
# - Apply CSV protocols (no BOM, correct newline handling)
# - Update state.json with merge count
''')

create_file("phase_5_assembly/deterministic_sanitizer.py", '''"""
Phase 5: Deterministic Sanitizer (DETERMINISTIC — NO LLM)

Post-merge sanitization pass. Enforces glossary compliance
across all output files using regex substitutions.

This script is AUTO-GENERATED from the locked glossary.
Run generate_sanitizer.py to regenerate.

Input:  Merged application files from merge_engine.py
Output: Sanitized application files with guaranteed glossary compliance
"""
# TODO: Import replacement rules from generate_sanitizer.py output
# - Read sanitizer replacement map
# - Scan all output files
# - Apply regex substitutions for known drift patterns
# - Report replacement counts
# - Update state.json
''')

# ============================================================
# PHASE 6: HUMAN REVIEW
# ============================================================

create_file("phase_6_human_review/corrections_log.json", json.dumps({
    "_meta": {
        "description": "Human review corrections log. Each correction feeds back into the glossary governance loop.",
        "created_at": None,
        "review_count": 0
    },
    "corrections": []
}, indent=2, ensure_ascii=False))

# ============================================================
# PHASE 7: ENGINE VALIDATION
# ============================================================

create_file("phase_7_engine_validation/protocol_check.py", '''"""
Phase 7: Engine Validation / Protocol Check (DETERMINISTIC — NO LLM)

Final gate before production release. Validates all output files
against Application's fragile CSV parser requirements.

Checks:
1. No UTF-8 BOM (Byte Order Mark) — Application's parser crashes on these
2. Correct newline semantics (preserve actual newlines in text fields)
3. No duplicate row keys
4. Column count matches header for every row
5. All required files present in plugin folder structure

Input:  Complete plugin folder
Output: Pass/Fail report with specific violations listed
"""
# TODO: Implement validation checks
# - Scan all CSV files for BOM bytes (EF BB BF)
# - Verify row/column integrity
# - Check for duplicate keys per file
# - Validate plugin_info.json structure
# - Update state.json with pass/fail counts
''')

# ============================================================
# README.md (root) — already exists at README.md.md, create proper one
# ============================================================

# Print summary
print(f"Created {len(created)} files:")
for f in created:
    print(f"  ✅ {f}")

if skipped:
    print(f"\nSkipped {len(skipped)} existing files:")
    for f in skipped:
        print(f"  ⏭️ {f}")
