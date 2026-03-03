from __future__ import annotations
import asyncio
import io
import wave
import time
from typing import List
import numpy as np

async def calibrate_noise(engine, seconds: float = 0.8) -> float:
    vals = []
    blocks = int(seconds * 1000 / engine.block_ms)

    for _ in range(12):
        if engine.input_queue.empty():
            break
        try:
            engine.input_queue.get_nowait()
        except Exception:
            break

    for _ in range(blocks):
        try:
            chunk = await asyncio.wait_for(engine.input_queue.get(), timeout=0.25)
            r = float(np.sqrt(np.mean(chunk * chunk) + 1e-12))
            vals.append(r)
        except asyncio.TimeoutError:
            break

    return float(np.mean(vals)) if vals else 0.002

async def vad_listen(engine, noise_rms: float, *, debug_save_audio: bool = False, debug_path: str = "debug_input.wav") -> bytes:
    base_noise = min(noise_rms, 0.05)
    start_thresh = max(0.0025, base_noise * 1.4)
    end_thresh = start_thresh * 0.75

    silence_limit = 0.55
    max_duration = 8.0
    min_speech_len = 0.20
    max_wait_for_start = 2.2

    for _ in range(6):
        if engine.input_queue.empty():
            break
        try:
            engine.input_queue.get_nowait()
        except Exception:
            break

    preroll = list(engine.preroll_buffer)
    frames: List[np.ndarray] = []
    speech_started = False
    silence_start = None
    t0 = time.time()

    while True:
        now = time.time()
        if not speech_started and (now - t0) > max_wait_for_start:
            return b""

        chunk = await engine.input_queue.get()
        r = float(np.sqrt(np.mean(chunk * chunk) + 1e-12))

        if not speech_started:
            if r > start_thresh:
                speech_started = True
                frames.extend(preroll)
                frames.append(chunk)
        else:
            frames.append(chunk)
            if r < end_thresh:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > silence_limit:
                    break
            else:
                silence_start = None

            if len(frames) * engine.block_ms / 1000 > max_duration:
                break

    if not speech_started or not frames:
        return b""

    audio = np.concatenate(frames)
    dur = len(audio) / engine.mic_sr
    if dur < min_speech_len:
        return b""

    audio_i16 = (np.clip(audio, -1.0, 1.0) * 32767.0).astype(np.int16)

    if debug_save_audio:
        with wave.open(debug_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(engine.mic_sr)
            wf.writeframes(audio_i16.tobytes())

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(engine.mic_sr)
        wf.writeframes(audio_i16.tobytes())
    return buf.getvalue()