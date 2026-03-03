import re
from typing import Optional

SUPPORTED = ("en-IN", "hi-IN", "gu-IN", "mr-IN")

def clamp_lang(lang: str) -> str:
    return lang if lang in SUPPORTED else "en-IN"

def normalize_detected_lang(detected: Optional[str], text: str, last_lang: str = "en-IN") -> str:
    if detected:
        d = detected.lower()
        if "hi" in d: return "hi-IN"
        if "gu" in d: return "gu-IN"
        if "mr" in d: return "mr-IN"
        if "en" in d: return "en-IN"

    if any("\u0a80" <= c <= "\u0aff" for c in text):  # Gujarati
        return "gu-IN"

    if any("\u0900" <= c <= "\u097f" for c in text):  # Devanagari (hi/mr)
        if last_lang in ("hi-IN", "mr-IN"):
            return last_lang
        return "hi-IN"

    if re.search(r"[A-Za-z]", text):
        return "en-IN"

    return last_lang if last_lang in SUPPORTED else "en-IN"