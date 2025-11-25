# src/speech/stt/recognizer_offline.py
import json, queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer
from .config import MIC_DEVICE_INDEX, DEFAULT_SECONDS

MODEL_PATH = "models/vosk/de/vosk-model-de-0.21"
SAMPLE_RATE = 16000

def transcribe_offline(seconds: int | None = None, device_index: int | None = None, show_partials: bool = True) -> str:
    """Offline-STT mit Vosk."""
    seconds = seconds or DEFAULT_SECONDS
    device_index = device_index if device_index is not None else MIC_DEVICE_INDEX

    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)

    q = queue.Queue()

    def _callback(indata, frames, time, status):
        if status:
            print("Audio-Status:", status)
        q.put(bytes(indata))

    text_final = ""
    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=_callback,
        device=device_index
    ):
        duration_ms = int(seconds * 1000)
        step_ms = 200
        for _ in range(duration_ms // step_ms):
            sd.sleep(step_ms)
            while not q.empty():
                data = q.get()
                if rec.AcceptWaveform(data):
                    pass
                elif show_partials:
                    part = rec.PartialResult()
                    try:
                        ptxt = json.loads(part).get("partial", "")
                        if ptxt:
                            print("…", ptxt)
                    except Exception:
                        pass

        final = rec.FinalResult()
        try:
            text_final = json.loads(final).get("text", "").strip()
        except Exception:
            text_final = ""

    return text_final