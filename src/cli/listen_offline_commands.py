# src/cli/listen_offline_commands.py
import json, queue
import sounddevice as sd
from vosk import Model, KaldiRecognizer

MODEL_PATH = "models/vosk/de/vosk-model-small-de-0.15"
SAMPLE_RATE = 16000

# Liste deiner Befehle/Wörter
COMMANDS = [
    "bobby", "stopp", "stop", "vorwärts", "rückwärts", "links", "rechts",
    "hallo", "ja", "nein"
]

def main():
    print("🎤 Sag einen Befehl (offline, 6s)…")
    model = Model(MODEL_PATH)
    # Grammatik / Phrases als JSON-String
    grammar = json.dumps(COMMANDS, ensure_ascii=False)
    rec = KaldiRecognizer(model, SAMPLE_RATE, grammar)

    q = queue.Queue()

    def _callback(indata, frames, time, status):
        if status:
            print("Audio-Status:", status)
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype="int16",
                           channels=1, callback=_callback, device=1):
        sd.sleep(6000)

        while not q.empty():
            data = q.get()
            rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())
        text = (result.get("text") or "").strip()
        if text:
            print("✅ Befehl erkannt:", text)
        else:
            print("❌ Kein Befehl erkannt. Probiere: 'Bobby', 'Stopp', 'links', …")

if __name__ == "__main__":
    main()
