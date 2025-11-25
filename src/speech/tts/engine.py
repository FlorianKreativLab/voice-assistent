# src/speech/tts/engine.py
import os, shutil, subprocess, tempfile
from ...audio.gate import speaking_guard
from .piper_voices import get_voice

def _first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None

# 1) ENV-Override (falls gesetzt), 2) dein genauer Pfad, 3) evtl. bin/piper, 4) PATH
PIPER_ENV = os.environ.get("PIPER_BIN")
PIPER_CANDIDATES = [
    PIPER_ENV,
    os.path.expanduser("~/Desktop/data/projekte/bobbi1.0/tools/piper"),             # <- DEIN PFAD
    os.path.expanduser("~/Desktop/data/projekte/bobbi1.0/tools/piper/bin/piper"),   # falls Bundle
    shutil.which("piper"),
]
PIPER_BIN = _first_existing(PIPER_CANDIDATES)

def speak(text: str, voice_hint: str = "", rate: int = 185, timeout_s: float = 30):
    voice = get_voice(voice_hint)
    if not PIPER_BIN:
        print("[TTS] Piper-Binary nicht gefunden. Kandidaten waren:")
        for c in PIPER_CANDIDATES: print("  -", c or "<None>")
        print("[TTS-Fallback]", text)
        return
    if not os.path.exists(voice.model):
        print("[TTS] Piper-Modell fehlt:", voice.model)
        print("[TTS-Fallback]", text)
        return

    with speaking_guard(hold_after_s=1.0):
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            wav = tmp.name
        try:
            cmd = [PIPER_BIN, "--model", voice.model, "--output_file", wav]
            res = subprocess.run(cmd, input=text.encode("utf-8"),
                                 timeout=timeout_s, capture_output=True, check=False)

            ok = os.path.exists(wav) and os.path.getsize(wav) >= 44
            if res.returncode != 0 or not ok:
                print("[TTS:ERR] Piper fehlgeschlagen (rc =", res.returncode, ")")
                if res.stderr: print("[TTS:STDERR]", res.stderr.strip())
                print("[TTS-Fallback]", text)
                return

            player = shutil.which("afplay") or "/usr/bin/afplay"
            subprocess.run([player, wav], check=False)
        finally:
            try: os.remove(wav)
            except Exception: pass