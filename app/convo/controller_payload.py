from typing import List, Dict

def build_controller_payload(customer: dict, lang_hint: str, last_turns: List[dict], latest_user: str) -> str:
    hist = "\n".join([f"{t['role'].upper()}: {t['text']}" for t in last_turns])
    return f"""
language_code: {lang_hint}

customer_name: {customer['customer_name']}
loan_type: {customer['loan_type']}
emi_amount: {customer['emi_amount']}
due_date: {customer['due_date']}

Conversation history (last turns):
{hist}

Latest user transcript:
{latest_user}

Instruction:
Reply ONLY in language_code above (en-IN / hi-IN / gu-IN / mr-IN).
""".strip()