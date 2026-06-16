import json
import os
import csv
import sys
import time

try:
    # Add root dir to sys.path to ensure pluginule resolution
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from phase_3_translation.llm_client import batch_translate_sync
    HAS_LLM = True
except Exception as e:
    print(f"Error importing llm_client: {e}")
    HAS_LLM = False

def translate_templates():
    input_path = "data/extracted_templates.json"
    output_path = "data/strings/dynamic_ui.csv"
    os.makedirs("data/strings", exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as f:
        templates = json.load(f)

    if not HAS_LLM:
        print("LLM client not available. Cannot perform dynamic translation.")
        return

    translations = []
    
    # We will translate in batches of 20
    batch_size = 20
    batches = [templates[i:i + batch_size] for i in range(0, len(templates), batch_size)]

    for i, batch in enumerate(batches):
        print(f"Translating batch {i+1}/{len(batches)}...")
        
        # Prepare batch for llm_client
        llm_input = []
        for item in batch:
            context = item.get("context", "")
            original = item["template"]
            # Encode context info
            context_str = f"{item['object']}.{item['method']}"
            
            llm_input.append({
                "source_text": original,
                "context_tag": context_str,
                "chunk_type": "dynamic_ui",
            })
            
        try:
            results = batch_translate_sync(llm_input)
            
            for orig_item, res_item in zip(batch, results):
                translations.append({
                    "original": orig_item["template"],
                    "japanese": res_item.get("translation", orig_item["template"]),
                    "regex": orig_item["regex"]
                })
        except Exception as e:
            print(f"Error translating batch: {e}")
            # Fallback
            for item in batch:
                translations.append({
                    "original": item["template"],
                    "japanese": item["template"],
                    "regex": item["regex"]
                })

    with open(output_path, "w", encoding="utf-8", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["original", "japanese", "regex"])
        writer.writeheader()
        writer.writerows(translations)

    print(f"Translated {len(translations)} templates to {output_path}")

if __name__ == "__main__":
    translate_templates()
