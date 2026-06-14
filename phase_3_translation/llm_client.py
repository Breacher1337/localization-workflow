import os
import json
import time
import asyncio
from google import genai
from google.genai import types
from google.genai.errors import APIError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

# Initialize API
API_KEY = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY) if API_KEY else None

# Use Gemini 2.5 Flash for all translations as requested
PLUGINEL_NAME = "gemini-2.5-flash"
RATE_LIMIT_DELAY = 4.5  # Seconds to wait between batches (15 RPM = 4 seconds, so 4.5 is safe)

class QuotaExhaustedError(Exception):
    """Raised when the daily quota is exhausted or rate limit is extreme."""
    pass

@retry(
    wait=wait_exponential(multiplier=2, min=5, max=60),
    stop=stop_after_attempt(4),
    retry=retry_if_exception_type(APIError),
    reraise=True
)
async def _call_gemini(prompt, system_instruction):
    return await client.aio.pluginels.generate_content(
        pluginel=PLUGINEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            system_instruction=system_instruction,
            temperature=0.3,
        )
    )

async def batch_translate(chunks):
    """
    Takes a list of chunk dicts.
    Constructs a batch prompt, calls Gemini 1.5 Flash, and returns the translated chunks.
    Raises QuotaExhaustedError if the daily limit is hit or it repeatedly fails.
    """
    if not chunks or not client:
        return chunks

    # Filter chunks that actually need translation
    to_translate = []
    for c in chunks:
        if c.get("translation") and c["translation"] != c["source_text"]:
            continue
        to_translate.append(c)

    if not to_translate:
        return chunks

    # Construct the payload
    prompt_payload = {}
    for i, chunk in enumerate(to_translate):
        prompt_payload[str(i)] = {
            "source_text": chunk["source_text"],
            "context_tag": chunk.get("context_tag", "unknown"),
            "chunk_type": chunk.get("chunk_type", "unknown")
        }

    system_instruction = (
        "You are an expert English-to-Japanese translator for the application Application. "
        "You will receive a JSON object containing strings to translate. "
        "Each item has a 'source_text', a 'context_tag' indicating its usage, and a 'chunk_type'. "
        "Translate the 'source_text' to Japanese naturally, keeping the context in mind. "
        "If it is a UI element or Group name, translate it as a noun. "
        "Maintain any placeholders like __G0__ exactly as they are. "
        "Return a JSON object where keys match the input keys, and the values are the translated strings."
    )

    prompt = f"Translate the following:\n{json.dumps(prompt_payload, ensure_ascii=False, indent=2)}"

    try:
        response = await _call_gemini(prompt, system_instruction)
        result_json = json.loads(response.text)
        
        # Map back to chunks
        for i, chunk in enumerate(to_translate):
            translated_text = result_json.get(str(i), chunk["source_text"])
            chunk["translation"] = translated_text
            
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "exhausted" in err_str:
            raise QuotaExhaustedError(f"API Quota Exhausted or Extreme Rate Limit: {e}")
        else:
            print(f"  [ERROR] Gemini Batch Translation Failed: {e}")
            # On failure, fallback to returning original text for this batch so pipeline doesn't halt
            for chunk in to_translate:
                if "translation" not in chunk:
                    chunk["translation"] = chunk["source_text"]

    await asyncio.sleep(RATE_LIMIT_DELAY)
    return chunks

def batch_translate_sync(batch):
    """Synchronous wrapper for processing a single batch"""
    if not API_KEY:
        for chunk in batch:
            if "translation" not in chunk:
                chunk["translation"] = chunk["source_text"]
        return batch
    
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_closed():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
    return loop.run_until_complete(batch_translate(batch))
