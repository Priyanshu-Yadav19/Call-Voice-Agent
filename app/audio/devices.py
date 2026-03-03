from __future__ import annotations
from typing import Optional
import sounddevice as sd

def get_device_index(kind: str, env_idx: Optional[int]) -> Optional[int]:
    if env_idx is not None:
        try:
            info = sd.query_devices(env_idx, kind)
            if info["max_" + kind + "_channels"] > 0:
                return env_idx
        except Exception:
            pass

    try:
        return sd.default.device[0 if kind == "input" else 1]
    except Exception:
        pass

    for i, dev in enumerate(sd.query_devices()):
        if dev["max_" + kind + "_channels"] > 0:
            return i
    return None

def get_output_samplerate(out_dev: Optional[int], fallback: int = 48000) -> int:
    try:
        info = sd.query_devices(out_dev, "output")
        return int(float(info.get("default_samplerate", fallback)))
    except Exception:
        return fallback