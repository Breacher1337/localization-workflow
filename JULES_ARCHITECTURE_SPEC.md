# Jules Architecture Specification: Agentic Codebase Localization

## Overview
This document outlines the architectural transition from offline static file scraping to an **Automated Codebase Static Analysis & Dynamic Bytecode Injection Engine**. The intent is to resolve persistent localization issues in Application, particularly where English text remains visible because of dynamic string generation, concatenations (like `womanHeOrShe`), and dynamically injected templates (`%s hazard rating`).

As the primary repository automation system, **Jules** is tasked with scanning the base application's Java codebase to discover these templates and generating the necessary Javassist bytecode hooks to intercept them at runtime.

## Core Directives for Jules

### 1. Static Analysis and AST Parsing
Jules must implement an automated scanning routine against the base application's source code (e.g., extracting from `legacyapp.api.zip` and decompiled `legacyapp_obf.jar`).
- Focus on extracting calls to UI rendering components: `TooltipMakerAPI.addPara`, `TextPanelAPI.addParagraph`, `LabelAPI.setText`, and variable string replacements like `StringHelper.getString`.
- Traverse the data flow to identify string concatenations. Convert these into tokenized templates (e.g., `+{0}% hazard rating`).

### 2. Bytecode Injection Generation
The current `AgentMain.java` is limited to an exact-match `TR.get()` lookup. 
- Jules must auto-generate advanced `insertBefore` Javassist hooks for `AgentMain.java`.
- These hooks will specifically target the identified rendering methods, utilizing Regular Expressions or pattern matching to replace tokens in dynamic strings before they hit the rendering engine.

### 3. Translation Pipeline Discretion
**Jules has the freedom to choose the translation method:**
- Jules may use the existing LLM pipeline (utilizing `gemma-4-26b-a4b-it` via `llm_client.py` with the 4.5s rate limit delay). If using the LLM, Jules must provide the Java source context (the surrounding 3-5 lines) so the LLM understands the variables and preserves tokens.
- Alternatively, Jules may opt to use its own translation methods, dictionaries, or localized heuristics if deemed more efficient or accurate for pattern matching.

### 4. Agentic Process Synchronization
Jules must ensure that the auto-generated translations and regex patterns synchronize correctly with `JPTranslator.java` at runtime. The `JPTranslator.init()` method needs to be expanded to parse a new pattern-based CSV format (e.g., `dynamic_ui.csv`).

## Wrap-up of the "main" Branch
This specification marks the end of the manual local scraping agent's responsibilities. The `main` branch has been finalized with the latest LLM configuration (`gemma-4-26b` defensive rate limiting) and the final static `scrape_untranslated_final.py` scripts. 
All future automated codebase scraping and bytecode generation should proceed on the `jules-static` branch.
