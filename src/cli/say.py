# src/cli/say.py

import argparse
from ..speech.tts.engine import speak

def main():
    parser = argparse.ArgumentParser(description="Sag einen Text mit TTS.")
    parser.add_argument("text", help="Was soll gesagt werden?")
    parser.add_argument(
        "--voice",
        default="Anna",               # <- Standard ist jetzt Anna
        help="Stimmenname (z.B. Anna, Markus). Standard: Anna"
    )
    parser.add_argument("--rate", type=int, default=180, help="Sprechgeschwindigkeit")
    parser.add_argument("--volume", type=float, default=1.0, help="Lautstärke 0.0 - 1.0")
    args = parser.parse_args()

    # voice_hint = immer der gewünschte Name (Standard: Anna)
    speak(args.text, voice_hint=args.voice, rate=args.rate, volume=args.volume)

if __name__ == "__main__":
    main()