# src/cli/listen.py
import argparse
from ..speech.stt.config import MIC_DEVICE_INDEX, DEFAULT_SECONDS
from ..speech.stt.recognizer_offline import transcribe_offline
from ..speech.stt.recognizer_online import transcribe_online

import os, sys
print("DEBUG __package__ =", __package__)
print("DEBUG cwd =", os.getcwd())
print("DEBUG sys.path[0] =", sys.path[0])

def main():
    parser = argparse.ArgumentParser(description="Sprache -> Text (offline oder online).")
    parser.add_argument("--mode", choices=["offline", "online"], default="offline", help="Erkenner-Modus")
    parser.add_argument("--seconds", type=int, default=DEFAULT_SECONDS, help="Aufnahme-Dauer in Sekunden")
    parser.add_argument("--device", type=int, default=None, help="Mikrofon-Index (nur offline/Vosk)")
    parser.add_argument("--lang", default="de-DE", help="Sprache für Online (z.B. de-DE)")
    args = parser.parse_args()

    if args.mode == "offline":
        print(f"🎤 (OFFLINE) Bitte sprich jetzt (max {args.seconds}s)...")
        text = transcribe_offline(seconds=args.seconds, device_index=args.device or MIC_DEVICE_INDEX, show_partials=True)
    else:
        text = transcribe_online(seconds=args.seconds, language=args.lang)

    if text:
        print("✅ Erkannt:", text)
    else:
        print("❌ Nichts verstanden.")

if __name__ == "__main__":
    main()