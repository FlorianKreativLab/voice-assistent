# src/speech/stt/recognizer_vosk_inline.py
# Ziel: ganze Sätze robust erkennen (ohne Internet), inkl. N-Best-Auswahl.

import json
from vosk import Model, KaldiRecognizer

from .vad_record import record_until_silence
try:
    from .config import MIC_DEVICE_INDEX
except Exception:
    MIC_DEVICE_INDEX = None

# === Wähle HIER dein Modell ===
# Besser (empfohlen): großes deutsches Modell
MODEL_PATH  = "models/vosk/de/vosk-model-de-0.21"
# Oder dein aktuelles kleines:
# MODEL_PATH  = "models/vosk/de/vosk-model-small-de-0.15"

SAMPLE_RATE = 16000

_model = None
def _get_model():
    global _model
    if _model is None:
        _model = Model(MODEL_PATH)
    return _model

def _pick_best_text(final_json: dict) -> str:
    """
    Nimmt das beste Ergebnis:
      1) höchste 'confidence' in alternatives
      2) bei Gleichstand: längster Text
      3) sonst fallback: final_json['text']
    """
    alts = final_json.get("alternatives") or []
    if alts:
        # Confidence kann fehlen -> dann 0.0
        def keyfn(a):
            return (float(a.get("confidence") or 0.0), len(a.get("text") or ""))
        best = max(alts, key=keyfn)
        return (best.get("text") or "").strip()
    return (final_json.get("text") or "").strip()

def transcribe_until_silence(
    max_seconds: float = 12.0,   # etwas mehr Zeit für ganze Sätze
    silence_ms: int = 700,       # 600–900: Ende der Sprache
    rms_threshold: float = 0.012,
    device_index: int | None = None
) -> str:
    """
    Hört bis Stille (oder max_seconds) und transkribiert den ganzen Satz.
    Nutzt N-Best der Vosk-Alternativen zur Qualitätsverbesserung.
    """
    audio_bytes = record_until_silence(
        max_seconds=max_seconds,
        silence_ms=silence_ms,
        rms_threshold=rms_threshold,
        device_index=device_index or MIC_DEVICE_INDEX,
    )
    if not audio_bytes:
        return ""

    rec = KaldiRecognizer(_get_model(), SAMPLE_RATE)
    rec.SetWords(True)
    # WICHTIG: mehrere Alternativen erlauben
    try:
        rec.SetMaxAlternatives(3)
    except AttributeError:
        # ältere vosk-Versionen haben das evtl. nicht – dann einfach weiter
        pass

    # Audio in handlichen Blöcken füttern
    CHUNK = 4000
    for i in range(0, len(audio_bytes), CHUNK):
        rec.AcceptWaveform(audio_bytes[i:i+CHUNK])

    try:
        final = json.loads(rec.FinalResult() or "{}")
    except Exception:
        return ""

    text = _pick_best_text(final)

    # Mini-Aufhübschung (erstes Wort groß, Punkt am Ende wenn fehlt)
    if text:
        t = text.strip()
        t = t[0:1].upper() + t[1:]
        if t and t[-1] not in ".!?":
            t += "."
        return t
    return ""