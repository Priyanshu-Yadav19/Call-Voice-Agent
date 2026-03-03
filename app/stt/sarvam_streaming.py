from __future__ import annotations
import asyncio
import base64
from typing import Any, Optional, Tuple
from sarvamai import AsyncSarvamAI

def _extract_text_from_stt_msg(msg: Any) -> str:
    if isinstance(msg, dict):
        if (msg.get("text") or "").strip():
            return (msg.get("text") or "").strip()
        data = msg.get("data")
        if isinstance(data, dict) and (data.get("transcript") or "").strip():
            return (data.get("transcript") or "").strip()
    if hasattr(msg, "data"):
        d = getattr(msg, "data")
        if isinstance(d, dict) and (d.get("transcript") or "").strip():
            return (d.get("transcript") or "").strip()
        if hasattr(d, "transcript"):
            val = getattr(d, "transcript") or ""
            if str(val).strip():
                return str(val).strip()
    return ""

def _extract_lang_from_stt_msg(msg: Any) -> Optional[str]:
    if isinstance(msg, dict):
        for k in ("language_code", "detected_language_code"):
            v = msg.get(k) or (msg.get("data") or {}).get(k)
            if v:
                return str(v)
    if hasattr(msg, "data"):
        d = getattr(msg, "data")
        if isinstance(d, dict):
            for k in ("language_code", "detected_language_code"):
                if d.get(k):
                    return str(d.get(k))
        else:
            for k in ("language_code", "detected_language_code"):
                if hasattr(d, k) and getattr(d, k):
                    return str(getattr(d, k))
    return None

class SarvamStreamingSTT:
    def __init__(self, api_key: str, sample_rate: int = 16000, model: str = "saaras:v3"):
        self.client = AsyncSarvamAI(api_subscription_key=api_key)
        self.sample_rate = sample_rate
        self.model = model
        self._cm = None
        self.ws = None
        self._lock = asyncio.Lock()

    async def connect(self):
        self._cm = self.client.speech_to_text_streaming.connect(
            model=self.model,
            mode="transcribe",
            language_code="unknown",
            sample_rate=self.sample_rate,
            flush_signal=True,
            input_audio_codec="wav",
        )
        self.ws = await self._cm.__aenter__()
        return self

    async def close(self):
        try:
            if self._cm:
                await self._cm.__aexit__(None, None, None)
        except Exception:
            pass

    async def transcribe_wav(self, wav_bytes: bytes, timeout_sec: float) -> Tuple[str, Optional[str]]:
        if not wav_bytes:
            return "", None
        audio_b64 = base64.b64encode(wav_bytes).decode("utf-8")

        async with self._lock:
            async def _do():
                await self.ws.transcribe(audio=audio_b64, encoding="audio/wav", sample_rate=self.sample_rate)
                await self.ws.flush()

                final_text = ""
                final_lang = None
                async for msg in self.ws:
                    if not final_lang:
                        final_lang = _extract_lang_from_stt_msg(msg)
                    t = _extract_text_from_stt_msg(msg)
                    if t:
                        final_text = t
                        break
                return final_text.strip(), final_lang

            try:
                return await asyncio.wait_for(_do(), timeout=timeout_sec)
            except Exception:
                return "", None