import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

SUPPORTED_LANGS = ("en-IN", "hi-IN", "gu-IN", "mr-IN")

@dataclass(frozen=True)
class AppConfig:
    sarvam_api_key: str

    # audio
    mic_sr: int
    tts_model_sr: int
    playback_gain: float
    tts_pace: float

    # barge-in
    barge_in_rms: float
    barge_in_hold_ms: int
    barge_in_min_play_ms: int
    echo_guard_ms: int

    # timeouts
    stt_timeout: float
    tts_chunk_idle_timeout: float
    tts_max_total_time: float
    tts_end_pad_ms: int

    # io / debug
    debug_save_audio: bool
    beep_test: bool
    input_device_index: int | None
    output_device_index: int | None

    # transcript
    save_transcript: bool
    transcript_dir: str
    max_turns: int

    # business
    bot_name: str
    org_name: str

    # customer
    customer_name: str
    loan_type: str
    emi_amount: int
    due_date: str

def _get_int(name: str, default: str) -> int:
    return int(os.getenv(name, default))

def _get_float(name: str, default: str) -> float:
    return float(os.getenv(name, default))

def _get_bool(name: str, default: str = "0") -> bool:
    return os.getenv(name, default) == "1"

def load_config() -> AppConfig:
    key = os.getenv("SARVAM_API_KEY", "").strip()
    if not key:
        raise RuntimeError("❌ SARVAM_API_KEY missing in .env")

    in_idx = os.getenv("INPUT_DEVICE_INDEX")
    out_idx = os.getenv("OUTPUT_DEVICE_INDEX")
    in_idx = int(in_idx) if in_idx else None
    out_idx = int(out_idx) if out_idx else None

    return AppConfig(
        sarvam_api_key=key,

        mic_sr=_get_int("MIC_SR", "16000"),
        tts_model_sr=_get_int("TTS_MODEL_SR", "24000"),
        playback_gain=_get_float("PLAYBACK_GAIN", "1.2"),
        tts_pace=_get_float("TTS_PACE", "1.0"),

        barge_in_rms=_get_float("BARGE_IN_RMS", "0.03"),
        barge_in_hold_ms=_get_int("BARGE_IN_HOLD_MS", "200"),
        barge_in_min_play_ms=_get_int("BARGE_IN_MIN_PLAY_MS", "450"),
        echo_guard_ms=_get_int("ECHO_GUARD_MS", "550"),

        stt_timeout=_get_float("STT_TIMEOUT", "8"),
        tts_chunk_idle_timeout=_get_float("TTS_CHUNK_IDLE_TIMEOUT", "2.5"),
        tts_max_total_time=_get_float("TTS_MAX_TOTAL_TIME", "30.0"),
        tts_end_pad_ms=_get_int("TTS_END_PAD_MS", "160"),

        debug_save_audio=_get_bool("DEBUG_SAVE_AUDIO", "0"),
        beep_test=_get_bool("BEEP_TEST", "0"),

        input_device_index=in_idx,
        output_device_index=out_idx,

        save_transcript=_get_bool("SAVE_TRANSCRIPT", "0"),
        transcript_dir=os.getenv("TRANSCRIPT_DIR", "transcripts"),
        max_turns=_get_int("MAX_TURNS", "40"),

        bot_name=os.getenv("BOT_NAME", "Vidya"),
        org_name=os.getenv("ORG_NAME", "Axis Bank"),

        customer_name=os.getenv("CUSTOMER_NAME", "Rohit Sharma"),
        loan_type=os.getenv("LOAN_TYPE", "Personal Loan"),
        emi_amount=_get_int("EMI_AMOUNT", "12500"),
        due_date=os.getenv("DUE_DATE", "2026-02-20"),
    )