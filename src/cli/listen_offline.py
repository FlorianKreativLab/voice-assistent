# src/cli/listen_offline.py
from ..speech.stt.recognizer_offline import transcribe_offline

def main():
    print("🎤 Bitte sprich jetzt (offline, 10s)...")
    text = transcribe_offline(seconds=10)
    if text:
        print("✅ Erkannt (offline):", text)
    else:
        print("❌ Nichts verstanden (offline).")

if __name__ == "__main__":
    main()
