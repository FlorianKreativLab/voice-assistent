# src/cli/what_do_you_hear.py
import json, queue, sounddevice as sd
from vosk import Model, KaldiRecognizer
from ..speech.stt.config import MIC_DEVICE_INDEX

MODEL_PATH = "models/vosk/de/vosk-model-small-de-0.15"
SAMPLE_RATE = 16000

def main():
    print("Sag bitte: 'Hallo Bobby' … (5s)")
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)
    rec.SetWords(True)
    q = queue.Queue()
    def cb(indata, frames, time, status):
        q.put(bytes(indata))
    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype="int16",
                           channels=1, callback=cb, device=MIC_DEVICE_INDEX):
        sd.sleep(5000)
        while not q.empty():
            rec.AcceptWaveform(q.get())
    print("FINAL:", json.loads(rec.FinalResult()).get("text",""))
if __name__ == "__main__":
    main()