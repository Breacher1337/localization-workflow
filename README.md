# Legacy Java Localization Workflow

This is a translation project, with the intent of the agentic workflow to expose the localized media to the Japanese audience. Localizing a hardcoded Java application without source access requires more than simple string replacement. This project evolved into an exercise in bytecode manipulation, encoding engineering, and designing AI orchestration pipelines.

This document serves as an engineering narrative detailing the evolution of this architecture—the challenges faced and the systems built to solve them.

## The Workflow

The original pipeline was designed to extract text data (CSVs and JSONs), use an LLM for translation, merge it back, and perform a Regex sweep to ensure terminology compliance.

```mermaid
flowchart TD
    classDef extract fill:#2a5078,stroke:#4a90e2,stroke-width:2px,color:#fff
    classDef ai fill:#5c2d73,stroke:#9b59b6,stroke-width:2px,color:#fff
    classDef strict fill:#782a2a,stroke:#e74c3c,stroke-width:2px,color:#fff
    classDef merge fill:#2d7348,stroke:#2ecc71,stroke-width:2px,color:#fff
    classDef glossary fill:#d68910,stroke:#f39c12,stroke-width:2px,color:#fff

    A[Raw Base Application Files\nCSVs, JSONs, Java] -->|Extraction Script| B(Translatable JSON Chunks)
    class A,B extract
    
    B --> C{Agentic AI\nLore Translator Subagents}
    G[(Master Glossary\nmaster_glossary.csv)] -.->|Provide Context & Tone| C
    class G glossary
    class C ai
    
    C -->|Output| D(Translated JSON Chunks)
    class D ai
    
    D -->|Merge Script| E[Translated Data Files\nin Plugin Folder]
    class E merge
    
    E --> F{Deterministic Sanitization\nRegex Sweep}
    G -.->|Strict Group Dictionary| F
    class F strict
    
    F -->|Replace Terminology Drift| H[Sanitized Data Files]
    class H merge
    
    H --> I{Engine Protocol Validation\nBOM & Newline Check}
    class I strict
    
    I -->|Pass| J(((Production Ready Output)))
    class J merge
```

While this architecture seemed sufficient, it failed when applied to the actual Java codebase.

## Challenges

### Structural Corruption
The CSVs contained logic columns alongside text. Basic extraction and merging corrupted these columns, causing the engine to crash.

To illustrate, consider how translatable columns (`name` and `desc`) are interleaved with critical JVM system paths and logic in the CSV architecture:
```csv
name,id,type,tags,...,plugin,ai,desc,sortOrder
SystemNode,node_01,TOGGLE,internal-,...,com.legacyapp.api.impl.nodes.SystemNode,...,Broadcast node identity; required for handshake.,100
```
Traditional translation engines translating columns like `type` (e.g. `TOGGLE`) or `plugin` (class names) immediately break JVM reflection and cause catastrophic crashes.

### Context Loss
Without structural context, the AI translated UI elements as narrative text, causing inconsistent formatting. Additionally, the text changed too much during translation for simple regex pattern matching to fix terminology drift.

Standard system error messages must be translated with high fidelity. Naive dictionary-based mapping drifts without structured schema verification.

Examples of Text Pairs:
- **Source:** `"Compiled for the wrong version of Java, change the compile target to Java 7"`
  **Target:** `"誤ったバージョンのJavaでコンパイルされています。コンパイルターゲットをJava 7に変更してください。"`
- **Source:** `"Are you sure? You'll lose any changes you've made to the settings."`
  **Target:** `"本当によろしいですか？変更した設定はすべて失われます。"`
- **Source:** `"Error in sound initialization, proceeding with sound disabled."`
  **Target:** `"サウンドの初期化でエラーが発生しました。サウンドを無効にして続行します。"`

### Hardcoded Strings
Translating data files was not enough. Many core UI strings were baked directly into the compiled Java bytecode (`.jar` files) without external localization files.

### Shift-JIS Encoding
The application relied on Shift-JIS encoding, while pluginern NLP tools use UTF-8. Transferring data without strict encoding governance caused data corruption, missing Byte Order Marks (BOMs), and broken newline semantics.

## The Workflow: Remastered

To solve these issues, I built a new agentic workflow. The focus shifted from translating text to building a restrictive environment where translation can safely occur.

```mermaid
flowchart TD
    classDef source fill:#1a1a2e,stroke:#4a5568,color:#e2e8f0,stroke-width:2px
    classDef prevent fill:#1b4332,stroke:#2d6a4f,color:#d8f3dc,stroke-width:2px
    classDef translate fill:#1d3557,stroke:#457b9d,color:#a8dadc,stroke-width:2px
    classDef detect fill:#5c2d73,stroke:#9b59b6,color:#e8daef,stroke-width:2px
    classDef correct fill:#78290f,stroke:#ff7b00,color:#ffddd2,stroke-width:2px
    classDef gate fill:#d4a017,stroke:#f1c40f,color:#1a1a2e,stroke-width:3px
    classDef output fill:#0b3d0b,stroke:#2ecc71,color:#d5f5e3,stroke-width:3px
    classDef human fill:#c0392b,stroke:#e74c3c,color:#fadbd8,stroke-width:2px

    subgraph P0["PHASE 0 · GLOSSARY GOVERNANCE"]
        direction TB
        G_RAW["Glossary Draft\n(Human + AI Candidates)"]:::source
        G_VALIDATE{"Glossary Validator Agent\n━━━━━━━━━━━\n• Cross-ref source application files\n• Flag ambiguous terms\n• Detect duplicate mappings\n• Verify contextual fit"}:::prevent
        G_HUMAN["Human Arbiter\nApproves / Rejects / Edits\nEach Entry"]:::human
        G_LOCKED[("Locked Glossary\n(Versioned, Immutable)")]:::prevent

        G_RAW --> G_VALIDATE
        G_VALIDATE -->|"Candidates + Flags"| G_HUMAN
        G_HUMAN -->|"Approved Entries"| G_LOCKED
    end

    subgraph P1["PHASE 1 · SOURCE EXTRACTION"]
        direction TB
        SRC_RAW["Raw Application Files\nCSVs, JSONs, JARs, Java"]:::source
        SRC_EXTRACT["Extraction Engine\n━━━━━━━━━━━\n• Separate translatable text\n• Preserve logic columns\n• Tag content types\n(UI / Lore / Procedural)"]:::translate
        SRC_CHUNKS["Tagged Source Chunks\n{type, file, column, row_id}"]:::translate

        SRC_RAW --> SRC_EXTRACT
        SRC_EXTRACT --> SRC_CHUNKS
    end

    subgraph P2["PHASE 2 · PRE-FLIGHT GATE"]
        direction TB
        PF_CHECK{"Pre-Flight Validator"}:::gate
        PF_PASS["Cleared for Translation"]:::prevent
        PF_FAIL["Blocked\nRoute to human for triage"]:::correct

        PF_CHECK -->|"Pass"| PF_PASS
        PF_CHECK -->|"Fail"| PF_FAIL
    end

    subgraph P3["PHASE 3 · AGENTIC TRANSLATION"]
        direction TB
        TR_AGENT{"Translator Subagents"}:::translate
        TR_OUTPUT["Raw Translated Chunks"]:::translate

        TR_AGENT --> TR_OUTPUT
    end

    subgraph P4["PHASE 4 · CRITIC LOOP"]
        direction TB
        CR_AGENT{"Critic Agent\n━━━━━━━━━━━\n• Glossary compliance check\n• Naturalness scoring\n• Placeholder integrity\n• Context consistency\n• Character limit check"}:::detect
        CR_PASS["Approved Chunks"]:::detect
        CR_REJECT["Rejected Chunks\n+ Specific Error Report"]:::correct

        CR_AGENT -->|"Score ≥ Threshold"| CR_PASS
        CR_AGENT -->|"Score < Threshold"| CR_REJECT
    end

    subgraph P5["PHASE 5 · ASSEMBLY"]
        direction TB
        MERGE["Merge Engine\n━━━━━━━━━━━\n• Reconstruct target files\n• Restore data structure"]:::translate
        SANITIZE{"Deterministic Sanitizer"}:::correct
        ASSEMBLED["Sanitized Output Files"]:::correct

        MERGE --> SANITIZE
        SANITIZE --> ASSEMBLED
    end

    subgraph P7["PHASE 7 · ENGINE VALIDATION"]
        direction TB
        ENGINE{"Engine Protocol Check"}:::gate
        READY((("Production\nReady Output"))):::output
        ENGINE_FAIL["Protocol Violation\nAuto-fix or block"]:::correct

        ENGINE -->|"Pass"| READY
        ENGINE -->|"Fail"| ENGINE_FAIL
    end

    G_LOCKED -->|"Glossary v1.x"| PF_CHECK
    SRC_CHUNKS --> PF_CHECK
    PF_PASS --> TR_AGENT
    G_LOCKED -.->|"Strict Reference"| TR_AGENT
    TR_OUTPUT --> CR_AGENT
    G_LOCKED -.->|"Compliance Baseline"| CR_AGENT
    CR_PASS --> MERGE
    ASSEMBLED --> ENGINE
    CR_REJECT -->|"Retry with\nerror context"| TR_AGENT
    ENGINE_FAIL -->|"Re-sanitize"| SANITIZE
    PF_FAIL -->|"Fix & Resubmit"| SRC_EXTRACT
```

### Pre-Flight Routing & Extraction
Phase 1 untangles text from application logic. It parses CSV headers and isolates the target string indices, leaving the surrounding data structure untouched. 

```python
# Snippet from Phase 3: Merging & Translation, highlighting structural preservation
with open(out_path, 'a' if start_idx > 1 else 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    if start_idx == 1:
        writer.writerow(headers)
        
    for row in reader[start_idx:]:
        if len(row) > name_idx and row[name_idx].strip():
            row[name_idx] = safe_translate(row[name_idx])
        if desc_idx != -1 and len(row) > desc_idx and row[desc_idx].strip():
            row[desc_idx] = safe_translate(row[desc_idx])
        if short_idx != -1 and len(row) > short_idx and row[short_idx].strip():
            row[short_idx] = safe_translate(row[short_idx])
        writer.writerow(row)
        f.flush()
```

### The Critic Loop
To solve context loss, a closed-loop critic system (Phase 4) was introduced. The output from Translator subagents is passed to a Critic Agent that scores the translation against an immutable Glossary from Phase 0. If the chunk fails context, length, or terminology checks, it is rejected and sent back with an error report.

### Javassist Bytecode Injection
To translate hardcoded strings inside `.jar` files, I built a bytecode manipulation toolset using the **Javassist** library. As the application boots up, a hook intercepts the rendering classes and injects logic directly into the Java methods. Instead of translating the bytecode offline, the tool pluginifies `setText` methods and class constructors at runtime to look up Japanese equivalents from an injected translation map.

```java
// Snippet from StaticInjector.java
String[] targetClasses = {
    "com.legacyapp.ui.d",
    "com.legacyapp.ui.impl.if",
    "com.legacyapp.ui.n",
    "com.legacyapp.ui.new",
    "com.legacyapp.ui.t"
};

// Javassist injection code for each class's setText(String) method:
String injectionCode = "{"
        + "  if ($1 != null && com.localizationplugin.Core.TR.containsKey($1)) {"
        + "      $1 = (String) com.localizationplugin.Core.TR.get($1);"
        + "  }"
        + "}";
```

## Feasibility Assessment

Can this achieve minimal mistranslations? **Yes.**
The workflow catches and fixes broad classes of errors, such as terminology drift, encoding corruption, and format violations. For a localization project, this is feasible and performs better than traditional fan translation methods.

Can this achieve zero mistranslations? **No.**
Zero mistranslation requires either a perfect AI that never makes contextual errors, or a complete human review of every translated string, which defeats the purpose of automation. This workflow produces output that is roughly 90-95% correct at the individual string level, with the sanitizer pushing the consistency of proper nouns close to 100%.

## Why build an Agentic Workflow?

The scale of the project demanded an automated approach. During extraction, the pipeline parses over 8,300+ text chunks across 49+ data files. Manually translating and validating this volume of text is not only time-consuming but also prone to human error, especially when dealing with complex CSV structures and the need for strict terminology compliance.

The agentic workflow allows for parallel processing of translation tasks, significantly reducing the time required to complete the project. Additionally, the integration of a critic loop ensures that the quality of translations is maintained, catching errors that may arise from context loss or terminology drift.

## Moral Lessons

### API Rate Limits
When running parallel subagents on thousands of text chunks, the main bottleneck was API rate limits. The Pre-Flight Validation gate (Phase 2) was implemented to prevent burning through rate limit quotas on malformed or untranslatable chunks.

### Non-Standard HJSON
The application utilized a custom HJSON configuration containing comments (`#`) and trailing commas that break standard JSON parsers:
```hjson
# Internal application caching settings
"enableScriptCaching":false, # caches compiled scripts in memory, faster startup time after first run
"doMemoryChecks":true, # will periodically check if memory is low and warn the user
},
```
Standard Python `json.loads` throws `json.decoder.JSONDecodeError` on this syntax. The extraction engine uses custom regular expressions to preprocess the HJSON into compliant RFC-8259 JSON before passing it to the translation agent.

### Composite Key Collisions
Several files used composite keys to differentiate entries. Naively translating keys often resulted in duplicate key attributes that represent different structural entities (e.g., a custom system pluginule vs. a registry entry):
```csv
id,type,text1
network_bridge,PLUGINULE,A deployable network bridge pluginule...
network_bridge,REGISTRY,Network bridge registry entry...
```
Translating the key `network_bridge` would cause duplicate key errors upon compilation. The extraction script generates a composite key `id|type` (e.g., `network_bridge|PLUGINULE` and `network_bridge|REGISTRY`) to guarantee uniqueness. The sanitizer required dynamic logic to detect and resolve these structural collisions.

## Summary
 
By separating the workflow into distinct layers, I reduced the risk of human error breaking the compiled source. This system bridges pluginern NLP tools and legacy Java environments, resulting in a stable deployment. The agentic workflow is not perfect, but it provides a scalable and efficient solution for localizing a complex application without source access. The integration of validation gates and critic loops ensures that the quality of translations is maintained while navigating the challenges of structural corruption, context loss, and encoding issues.
