from __future__ import annotations
import asyncio
import time
import collections
from typing import Optional, Deque
import numpy as np
import sounddevice as sd

class AudioEngine:
    """
    Owns input/output streams + barge-in state.
    No business logic here.
    """
    def __init__(
        self,
        mic_sr: int,
        out_sr: int,
        in_dev: Optional[int],
        out_dev: Optional[int],
        *,
        barge_in_rms: float,
        barge_in_hold_ms: int,
        barge_in_min_play_ms: int,
        echo_guard_ms: int,
        block_ms: int = 20,
        input_queue_max: int = 80,
        preroll_ms: int = 500,
        logger=None,
    ):
        self.mic_sr = mic_sr
        self.out_sr = out_sr
        self.in_dev = in_dev
        self.out_dev = out_dev
        self.block_ms = block_ms

        self.barge_in_rms = float(barge_in_rms)
        self.barge_in_hold_ms = int(barge_in_hold_ms)
        self.barge_in_min_play_ms = int(barge_in_min_play_ms)
        self.echo_guard_ms = int(echo_guard_ms)

        self.logger = logger

        self.input_block_size = int(mic_sr * block_ms / 1000)
        self.output_block_size = int(out_sr * block_ms / 1000)

        self.loop = asyncio.get_running_loop()
        self.input_queue: asyncio.Queue[np.ndarray] = asyncio.Queue(maxsize=input_queue_max)

        # barge-in state
        self.is_playing = False
        self.barge_in_triggered = False
        self.barge_in_hold_blocks = max(1, int(self.barge_in_hold_ms / self.block_ms))
        self.loud_block_count = 0

        self.noise_rms = 0.01
        self.barge_in_threshold = self.barge_in_rms

        self.echo_guard_until = 0.0
        self.playback_start_ts = 0.0

        # preroll for VAD
        self.preroll_maxlen = int(preroll_ms / self.block_ms)
        self.preroll_buffer: Deque[np.ndarray] = collections.deque(maxlen=self.preroll_maxlen)

        self.input_stream = sd.InputStream(
            samplerate=mic_sr,
            blocksize=self.input_block_size,
            channels=1,
            dtype="float32",
            device=in_dev,
            callback=self._input_callback,
            latency="low",
        )
        self.output_stream = sd.OutputStream(
            samplerate=out_sr,
            blocksize=self.output_block_size,
            channels=1,
            dtype="int16",
            device=out_dev,
            latency="low",
        )

    def start(self):
        self.input_stream.start()
        self.output_stream.start()
        if self.logger:
            self.logger.info("🎙️ Audio Engine Started")

    def stop(self):
        for s in (self.input_stream, self.output_stream):
            try:
                s.stop()
                s.close()
            except Exception:
                pass

    def set_noise_rms(self, noise_rms: float):
        self.noise_rms = float(noise_rms)
        # reduce false triggers
        self.barge_in_threshold = max(self.barge_in_rms, self.noise_rms * 3.2)

    def stop_playback_now(self):
        self.barge_in_triggered = True

    def _input_callback(self, indata, frames, time_info, status):
        audio_chunk = indata.copy()
        self.preroll_buffer.append(audio_chunk)

        # barge-in detection (only during playback)
        if self.is_playing and not self.barge_in_triggered:
            now = time.time()
            if now >= self.echo_guard_until and (now - self.playback_start_ts) * 1000.0 >= self.barge_in_min_play_ms:
                r = float(np.sqrt(np.mean(audio_chunk * audio_chunk) + 1e-12))
                if r > self.barge_in_threshold:
                    self.loud_block_count += 1
                    if self.loud_block_count >= self.barge_in_hold_blocks:
                        self.barge_in_triggered = True
                        self.loud_block_count = 0
                        if self.logger:
                            self.logger.info("🛑 BARGE-IN DETECTED")
                        try:
                            self.loop.call_soon_threadsafe(self.stop_playback_now)
                        except Exception:
                            pass
                else:
                    self.loud_block_count = 0

        def _push():
            try:
                self.input_queue.put_nowait(audio_chunk)
            except asyncio.QueueFull:
                try:
                    _ = self.input_queue.get_nowait()
                except Exception:
                    pass
                try:
                    self.input_queue.put_nowait(audio_chunk)
                except Exception:
                    pass

        try:
            if not self.loop.is_closed():
                self.loop.call_soon_threadsafe(_push)
        except Exception:
            pass