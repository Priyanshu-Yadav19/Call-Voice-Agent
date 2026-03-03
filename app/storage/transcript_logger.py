from __future__ import annotations
import os
import json
from datetime import datetime

class TranscriptLogger:
    def __init__(self, enabled: bool, out_dir: str = "transcripts"):
        self.enabled = enabled
        self.path = None
        self.f = None
        if not enabled:
            return
        os.makedirs(out_dir, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.path = os.path.join(out_dir, f"call_{ts}.jsonl")
        self.f = open(self.path, "a", encoding="utf-8")

    def log(self, role: str, text: str, **meta):
        if not self.enabled or not self.f:
            return
        rec = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "role": role,
            "text": (text or "").strip(),
            **meta,
        }
        self.f.write(json.dumps(rec, ensure_ascii=False) + "\n")
        self.f.flush()

    def close(self):
        try:
            if self.f:
                self.f.close()
        except Exception:
            pass