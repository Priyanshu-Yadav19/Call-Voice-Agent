import re

def is_repeat_request(text: str) -> bool:
    return bool(re.search(r"\brepeat\b|फिर से बोलो|फिरसे बोलो|ફરી કહો|परत सांगा", (text or ""), re.IGNORECASE))

def strip_assistant_text_prefix(s: str) -> str:
    s = (s or "").strip()
    s = re.sub(r"^\s*assistant_text\s*:\s*", "", s, flags=re.IGNORECASE).strip()
    return s

def language_guard(assistant_text: str, lang: str) -> str:
    """
    Last-line defense if the model violates script.
    """
    if lang == "gu-IN" and not any("\u0a80" <= c <= "\u0aff" for c in assistant_text):
        return "માફ કરશો, કૃપા કરીને ફરીથી કહેશો?"
    if lang in ("hi-IN", "mr-IN") and not any("\u0900" <= c <= "\u097f" for c in assistant_text):
        return "माफ़ कीजिए, कृपया दोबारा बोलेंगे?"
    if lang == "en-IN" and not re.search(r"[A-Za-z]", assistant_text):
        return "Sorry, could you please repeat?"
    return assistant_text