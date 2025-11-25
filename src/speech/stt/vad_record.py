# src/speech/stt/vad_record.py
# Ziel: Audio aufnehmen, bis Stille erkannt wird (oder max_seconds erreicht ist).
# -> VAD per RMS (Lautstärke). Kompatibel ohne 'nonlocal'.

import time
import queue
import numpy as np
import sounddevice as sd

# Optional: während TTS nicht aufnehmen (Half-Duplex). Falls Modul fehlt, dummy verwenden.
try:
    from ...audio.gate import is_speaking as _is_speaking
except Exception:
    def _is_speaking() -> bool:
        return False

try:
    from .config import MIC_DEVICE_INDEX
except Exception:
    MIC_DEVICE_INDEX = None

SAMPLE_RATE = 16000

def _rms(data: np.ndarray) -> float:
    """Root-Mean-Square = Lautstärkeindikator."""
    return float(np.sqrt(np.mean(np.square(data), dtype=np.float64)))

def record_until_silence(
    max_seconds: float = 8.0,
    silence_ms: int = 700,
    rms_threshold: float = 0.012,
    device_index: int | None = None
) -> bytes:
    """
    Nimmt Audio auf und stoppt, wenn 'silence_ms' am Stück unter 'rms_threshold' sind
    oder 'max_seconds' erreicht sind.
    Gibt Roh-Bytes (int16) zurück.
    """

    device_index = device_index if device_index is not None else MIC_DEVICE_INDEX

    blocksize = 1024                   # kleinere Blöcke -> niedrigere Latenz
    bytes_q: queue.Queue[bytes] = queue.Queue()
    last_voice_time = [time.time()]    # mutable Container statt 'nonlocal'
    start_time = time.time()

    def _cb(indata, frames, time_info, status):
        """Callback von sounddevice: prüft Lautstärke und legt Daten in Queue."""
        if status:
            # optional: print("Audio-Status:", status)
            pass

        # Wenn TTS/Heidi gerade spricht, verwerfe Eingangsframes komplett
        if _is_speaking():
            return

        # Daten als float32 [-1..1]
        arr = np.asarray(indata, dtype=np.float32).reshape(-1)
        level = _rms(arr)
        if level > rms_threshold:
            last_voice_time[0] = time.time()  # Stimme erkannt -> Reset

        # Konvertiere nach int16 und lege in Queue
        i16 = np.clip(arr, -1.0, 1.0) * 32767.0
        bytes_q.put(i16.astype(np.int16).tobytes())

    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        blocksize=blocksize,
        dtype="float32",
        channels=1,
        callback=_cb,
        device=device_index,
        latency="low"
    ):
        collected: list[bytes] = []
        poll_ms = 40  # alle 40 ms prüfen
        while True:
            # alles aus der Queue holen
            while not bytes_q.empty():
                collected.append(bytes_q.get())

            now = time.time()
            if (now - start_time) >= max_seconds:
                break

            # wenn seit 'silence_ms' ms keine Stimme
            if (now - last_voice_time[0]) * 1000.0 >= silence_ms:
                # kurze Hangover-Zeit, um das Satzende mitzunehmen
                time.sleep(0.12)
                while not bytes_q.empty():
                    collected.append(bytes_q.get())
                break

            time.sleep(poll_ms / 1000.0)

    return b"".join(collected)