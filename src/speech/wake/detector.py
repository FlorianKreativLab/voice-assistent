# src/speech/wake/detector.py
import json, queue, time
import sounddevice as sd
from vosk import Model, KaldiRecognizer

# Config sicher laden (sonst Defaults)
try:
    from ..stt.config import MIC_DEVICE_INDEX, DEFAULT_SECONDS
except Exception:
    MIC_DEVICE_INDEX, DEFAULT_SECONDS = None, 6

from ..tts.engine import speak

MODEL_PATH = "models/vosk/de/vosk-model-small-de-0.15"
SAMPLE_RATE = 16000

WAKE_TARGET = "heidi"      # das Zielwort
STEP_SEC     = 0.08    # häufiger prüfen (statt 0.10)
WINDOW_SEC   = 1.2     # etwas längeres Fenster (statt 1.0)
DEBOUNCE_SEC = 0.9     # etwas längere Sperre nach Treffer (gegen Doppel-Trigger)

# ---- Modell EINMAL laden ----
_model = None
def get_model():
    global _model
    if _model is None:
        _model = Model(MODEL_PATH)
    return _model

def _make_recognizer() -> KaldiRecognizer:
    rec = KaldiRecognizer(get_model(), SAMPLE_RATE)  # KEINE Grammatik -> freie Erkennung
    rec.SetWords(True)
    return rec

def _norm(s: str) -> str:
    return (s or "").strip().lower()

def _levenshtein(a: str, b: str) -> int:
    # kleine Edit-Distanz, ohne Extra-Pakete
    a, b = _norm(a), _norm(b)
    if a == b: return 0
    if not a:  return len(b)
    if not b:  return len(a)
    dp = list(range(len(b)+1))
    for i, ca in enumerate(a, 1):
        prev = dp[0]
        dp[0] = i
        for j, cb in enumerate(b, 1):
            cur = dp[j]
            cost = 0 if ca == cb else 1
            dp[j] = min(dp[j] + 1, dp[j-1] + 1, prev + cost)
            prev = cur
    return dp[-1]

def _is_wake_in(text: str) -> bool:
    """
    Treffer wenn:
      - 'bobby' als Teil vorkommt, oder
      - Levenshtein-Distanz <=1 (bobi/boby/…)
    """
    t = _norm(text)
    if not t:
        return False
    if WAKE_TARGET in t:
        return True
    # Wortweise prüfen (robust gegen 'hallo bobi')
    for w in t.split():
        if _levenshtein(w, WAKE_TARGET) <= 1:
            return True
    return False

def listen_for_wake(device_index=None, seconds: float = WINDOW_SEC, show_debug: bool = False) -> bool:
    device_index = device_index if device_index is not None else MIC_DEVICE_INDEX
    rec = _make_recognizer()
    q = queue.Queue()

    def _cb(indata, frames, time_info, status):
        if status and show_debug:
            print("Audio-Status:", status)
        q.put(bytes(indata))

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=1024,      # kleiner (statt 2048) → niedrigere Latenz
        dtype="int16",
        channels=1,
        latency="low",
        callback=_cb,
        device=MIC_DEVICE_INDEX
    ):
        # in mini-Schritten, damit wir Partials prüfen können
        steps = max(1, int(seconds * 1000 / 200))
        partial_hit = False
        for _ in range(steps):
            time.sleep(0.2)
            while not q.empty():
                data = q.get()
                if rec.AcceptWaveform(data):
                    # final wird unten gelesen
                    pass
                else:
                    # Partial prüfen
                    try:
                        part = json.loads(rec.PartialResult() or "{}").get("partial", "")
                    except Exception:
                        part = ""
                    if show_debug and part:
                        print("…", part)
                    if _is_wake_in(part):
                        partial_hit = True
                        if show_debug:
                            print("[wake] partial HIT")
                        # wir brechen NICHT sofort ab, damit das final auch lesen kann

        # Final prüfen
        try:
            final_text = json.loads(rec.FinalResult() or "{}").get("text", "")
        except Exception:
            final_text = ""
        if show_debug:
            print("[wake] final:", final_text)

        return partial_hit or _is_wake_in(final_text)

def wake_loop():
    print("👂 Warte auf Wakeword 'Bobby' (Strg+C zum Beenden)…")
    try:
        while True:
            woke = listen_for_wake(seconds=WINDOW_SEC, show_debug=False)
            if woke:
                speak("Ja, bitte?", voice_hint="Anna")
                time.sleep(1.0)  # Debounce
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("\n👋 Wake-Loop beendet.")