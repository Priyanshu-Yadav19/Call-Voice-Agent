import asyncio
import collections
import numpy as np

from app.config import load_config
from app.logging_setup import setup_logging

from app.audio.devices import get_device_index, get_output_samplerate
from app.audio.engine import AudioEngine
from app.audio.vad import calibrate_noise, vad_listen

from app.stt.sarvam_streaming import SarvamStreamingSTT
from app.tts.sarvam_streaming import SarvamStreamingTTS

from app.llm.prompts import VIDYA_SYSTEM_PROMPT
from app.llm.sarvam_chat import ConversationManager

from app.convo.language import clamp_lang, normalize_detected_lang
from app.convo.rules import is_repeat_request, strip_assistant_text_prefix, language_guard
from app.convo.controller_payload import build_controller_payload

from app.storage.transcript_logger import TranscriptLogger


async def main():
    cfg = load_config()
    logger = setup_logging()

    in_idx = get_device_index("input", cfg.input_device_index)
    out_idx = get_device_index("output", cfg.output_device_index)
    out_sr = get_output_samplerate(out_idx, fallback=48000)

    logger.info(f"Input device: {in_idx} | Output device: {out_idx}")
    logger.info(f"Output device SR: {out_sr} Hz | Sarvam TTS SR: {cfg.tts_model_sr} Hz (resample if different)")

    engine = AudioEngine(
        cfg.mic_sr, out_sr, in_idx, out_idx,
        barge_in_rms=cfg.barge_in_rms,
        barge_in_hold_ms=cfg.barge_in_hold_ms,
        barge_in_min_play_ms=cfg.barge_in_min_play_ms,
        echo_guard_ms=cfg.echo_guard_ms,
        logger=logger
    )
    engine.start()

    if cfg.beep_test:
        t = np.linspace(0, 0.25, int(out_sr * 0.25), endpoint=False)
        tone = (0.2 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
        engine.output_stream.write((tone * 32767).astype(np.int16))
        logger.info("🔊 Beep test played (BEEP_TEST=1)")

    tlog = TranscriptLogger(cfg.save_transcript, cfg.transcript_dir)
    if cfg.save_transcript:
        logger.info(f"📝 Transcript saving to: {tlog.path}")

    noise_rms = await calibrate_noise(engine, 0.9)
    engine.set_noise_rms(noise_rms)
    logger.info(f"Noise calibrated: {noise_rms:.5f} | barge_in_threshold={engine.barge_in_threshold:.5f}")

    stt = SarvamStreamingSTT(cfg.sarvam_api_key, sample_rate=cfg.mic_sr)
    await stt.connect()

    tts = SarvamStreamingTTS(
        cfg.sarvam_api_key,
        tts_model_sr=cfg.tts_model_sr,
        playback_gain=cfg.playback_gain,
        pace=cfg.tts_pace,
        idle_timeout=cfg.tts_chunk_idle_timeout,
        max_total_time=cfg.tts_max_total_time,
        end_pad_ms=cfg.tts_end_pad_ms,
        echo_guard_ms=cfg.echo_guard_ms,
        logger=logger
    )

    chat = ConversationManager(cfg.sarvam_api_key, VIDYA_SYSTEM_PROMPT)

    customer = {
        "customer_name": cfg.customer_name,
        "loan_type": cfg.loan_type,
        "emi_amount": cfg.emi_amount,
        "due_date": cfg.due_date,
    }

    turns = collections.deque(maxlen=20)
    last_bot_text = ""
    preferred_lang = "en-IN"

    opening = (
        f"Hi {customer['customer_name']}, I’m {cfg.bot_name} from {cfg.org_name}. "
        f"This is regarding your {customer['loan_type']}. Is it a good time to talk?"
    )
    last_bot_text = opening
    logger.info(f"🤖 BOT[{preferred_lang}]: {opening}")
    tlog.log("bot", opening, lang=preferred_lang)
    await tts.play(engine, opening, preferred_lang)
    turns.append({"role": "assistant", "text": opening})

    try:
        for _ in range(cfg.max_turns):
            logger.info("🎤 Listening…")
            wav_bytes = await vad_listen(engine, noise_rms, debug_save_audio=cfg.debug_save_audio)
            user_text, det = await stt.transcribe_wav(wav_bytes, timeout_sec=cfg.stt_timeout)
            user_text = (user_text or "").strip()
            if not user_text:
                continue

            preferred_lang = clamp_lang(normalize_detected_lang(det, user_text, last_lang=preferred_lang))
            logger.info(f"👤 USER[{preferred_lang}]: {user_text}")
            tlog.log("user", user_text, lang=preferred_lang, detected_lang=det)

            if is_repeat_request(user_text):
                await tts.play(engine, last_bot_text, preferred_lang)
                continue

            turns.append({"role": "user", "text": user_text})
            payload = build_controller_payload(customer, preferred_lang, list(turns)[-6:], user_text)

            raw = await chat.complete(payload)
            assistant_text = strip_assistant_text_prefix(raw) or (
                "Sorry, could you please repeat?" if preferred_lang == "en-IN" else "माफ़ कीजिए, कृपया दोबारा बोलेंगे?"
            )

            assistant_text = language_guard(assistant_text, preferred_lang)

            last_bot_text = assistant_text
            turns.append({"role": "assistant", "text": assistant_text})

            logger.info(f"🤖 BOT[{preferred_lang}]: {assistant_text}")
            tlog.log("bot", assistant_text, lang=preferred_lang)
            await tts.play(engine, assistant_text, preferred_lang)

            # update noise slowly
            new_noise = await calibrate_noise(engine, 0.25)
            noise_rms = 0.85 * noise_rms + 0.15 * new_noise
            engine.set_noise_rms(noise_rms)

    finally:
        try:
            await stt.close()
        except Exception:
            pass
        try:
            tlog.close()
        except Exception:
            pass
        engine.stop()


if __name__ == "__main__":
    asyncio.run(main())