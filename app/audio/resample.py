import numpy as np

def resample_i16(audio_i16: np.ndarray, src_sr: int, dst_sr: int) -> np.ndarray:
    if src_sr == dst_sr or audio_i16.size == 0:
        return audio_i16
    x = audio_i16.astype(np.float32)
    src_n = x.shape[0]
    dst_n = int(round(src_n * (dst_sr / src_sr)))
    if dst_n <= 1:
        return audio_i16[:0]
    src_idx = np.linspace(0.0, src_n - 1, num=dst_n, dtype=np.float32)
    idx0 = np.floor(src_idx).astype(np.int32)
    idx1 = np.minimum(idx0 + 1, src_n - 1)
    frac = src_idx - idx0
    y = (1.0 - frac) * x[idx0] + frac * x[idx1]
    return np.clip(y, -32768, 32767).astype(np.int16)