from __future__ import annotations
import asyncio
import base64
import time
import numpy as np
from sarvamai import AsyncSarvamAI, AudioOutput, EventResponse
from app.audio.resample import resample_i16

SUPPORTED_LANGS = ("en-IN", "hi-IN", "gu-IN", "mr-IN")

def clamp_lang(lang: str) -> str:
    return lang if lang in SUPPORTED_LANGS else "en-IN"

async def drain_input(engine, ms: int = 250):
    end = time.time() + (ms / 1000.0)
    while time.time() < end:
        try:
            engine.input_queue.get_nowait()
        except Exception:
            await asyncio.sleep(0.01)

async def _write_end_pad(engine, pad_ms: int):
    if pad_ms <= 0:
        return
    n = int(engine.out_sr * (pad_ms / 1000.0))
    if n <= 0:
        return
    zeros = np.zeros(n, dtype=np.int16)
    step = 1024
    for i in range(0, len(zeros), step):
        engine.output_stream.write(zeros[i:i + step])
        await asyncio.sleep(0.001)

class SarvamStreamingTTS:
    def __init__(
        self,
        api_key: str,
        *,
        model: str = "bulbul:v3",
        speaker: str = "roopa",
        tts_model_sr: int = 24000,
        playback_gain: float = 1.0,
        pace: float = 1.0,
        idle_timeout: float = 2.5,
        max_total_time: float = 30.0,
        end_pad_ms: int = 160,
        echo_guard_ms: int = 550,
        logger=None
    ):
        self.api_key = api_key
        self.model = model
        self.speaker = speaker
        self.tts_model_sr = tts_model_sr
        self.playback_gain = float(playback_gain)
        self.pace = float(pace)
        self.idle_timeout = float(idle_timeout)
        self.max_total_time = float(max_total_time)
        self.end_pad_ms = int(end_pad_ms)
        self.echo_guard_ms = int(echo_guard_ms)
        self.logger = logger

    async def play(self, engine, text: str, lang_code: str):
        text = (text or "").strip()
        if not text:
            return

        lang_code = clamp_lang(lang_code)
        client = AsyncSarvamAI(api_subscription_key=self.api_key)

        engine.is_playing = True
        engine.barge_in_triggered = False
        engine.loud_block_count = 0
        engine.echo_guard_until = time.time() + (self.echo_guard_ms / 1000.0)
        engine.playback_start_ts = time.time()

        chunk_count = 0
        byte_count = 0
        started = time.time()
        last_chunk_ts = time.time()
        got_any_audio = False

        try:
            async with client.text_to_speech_streaming.connect(model=self.model, send_completion_event=True) as ws:
                await ws.configure(
                    target_language_code=lang_code,
                    speaker=self.speaker,
                    pace=self.pace,
                    output_audio_codec="linear16",
                    speech_sample_rate=self.tts_model_sr,
                )
                await ws.convert(text)
                await ws.flush()

                aiter = ws.__aiter__()
                while True:
                    if engine.barge_in_triggered:
                        if self.logger:
                            self.logger.info("Playback stopped (barge-in) -> closing TTS stream")
                        try:
                            await ws.close()
                        except Exception:
                            pass
                        break

                    if (time.time() - started) > self.max_total_time:
                        if self.logger:
                            self.logger.warning("TTS max total time reached -> stopping")
                        try:
                            await ws.close()
                        except Exception:
                            pass
                        break

                    if got_any_audio and (time.time() - last_chunk_ts) > self.idle_timeout:
                        if self.logger:
                            self.logger.warning("TTS idle timeout -> stopping")
                        try:
                            await ws.close()
                        except Exception:
                            pass
                        break

                    try:
                        message = await asyncio.wait_for(aiter.__anext__(), timeout=self.idle_timeout)
                    except asyncio.TimeoutError:
                        if not got_any_audio and (time.time() - started) < max(5.0, self.idle_timeout):
                            continue
                        if self.logger:
                            self.logger.warning("TTS receive timeout -> stopping")
                        break
                    except StopAsyncIteration:
                        break

                    if isinstance(message, AudioOutput):
                        got_any_audio = True
                        last_chunk_ts = time.time()

                        chunk_count += 1
                        pcm_bytes = base64.b64decode(message.data.audio)
                        byte_count += len(pcm_bytes)

                        audio_np = np.frombuffer(pcm_bytes, dtype=np.int16)

                        if self.tts_model_sr != engine.out_sr:
                            audio_np = resample_i16(audio_np, self.tts_model_sr, engine.out_sr)

                        if self.playback_gain != 1.0:
                            audio_np = (audio_np.astype(np.float32) * self.playback_gain).clip(-32768, 32767).astype(np.int16)

                        step = 1024
                        for i in range(0, len(audio_np), step):
                            if engine.barge_in_triggered:
                                break
                            engine.output_stream.write(audio_np[i:i + step])
                            await asyncio.sleep(0.001)

                    elif isinstance(message, EventResponse):
                        if getattr(message.data, "event_type", "") == "final":
                            break

        except Exception as e:
            if self.logger:
                self.logger.error(f"TTS stream play error: {e}")

        finally:
            if self.logger:
                self.logger.info(f"TTS done chunks={chunk_count} total_bytes={byte_count}")
            engine.is_playing = False
            await asyncio.sleep(0.02)

            if got_any_audio and not engine.barge_in_triggered:
                await _write_end_pad(engine, self.end_pad_ms)

            if engine.barge_in_triggered:
                await drain_input(engine, 250)