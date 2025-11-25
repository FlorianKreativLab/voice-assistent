# src/speech/tts/piper_voices.py
# zentrale Stimmen-Liste für Piper

import os
from dataclasses import dataclass

BASE = os.path.expanduser("~/Desktop/data/projekte/bobbi1.0/models/piper")

@dataclass(frozen=True)
class PiperVoice:
    model: str           # .onnx
    config: str | None = None  # .onnx.json (optional, Piper liest cfg oft automatisch)
    # Feintuning (optional)
    noise_scale: float = 0.667
    length_scale: float = 1.0   # < 1.0 = schneller, > 1.0 = langsamer
    noise_w: float = 0.8

VOICES: dict[str, PiperVoice] = {
    # weiblich, schnell & natürlich (empfohlen)
    "kerstin-low": PiperVoice(
        model=os.path.join(BASE, "de_DE-kerstin-low.onnx"),
        config=os.path.join(BASE, "de_DE-kerstin-low.onnx.json"),
        length_scale=0.95
    ),
    # männlich, hohe Qualität
    "thorsten-high": PiperVoice(
        model=os.path.join(BASE, "de_DE-thorsten-high.onnx"),
        config=os.path.join(BASE, "de_DE-thorsten-high.onnx.json"),
        length_scale=1.0
    ),
    # sehr leicht/schnell – nur wenn du die Dateien hast
    "ramona-low": PiperVoice(
        model=os.path.join(BASE, "de_DE-ramona-low.onnx"),
        config=os.path.join(BASE, "de_DE-ramona-low.onnx.json"),
        length_scale=0.9
    ),
}

DEFAULT_VOICE = "kerstin-low"

def get_voice(name: str | None) -> PiperVoice:
    name = (name or DEFAULT_VOICE).lower().strip()
    return VOICES.get(name, VOICES[DEFAULT_VOICE])
