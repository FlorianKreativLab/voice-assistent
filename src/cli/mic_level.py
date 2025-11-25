# src/cli/mic_level.py
import numpy as np, sounddevice as sd, time
from ..speech.stt.config import MIC_DEVICE_INDEX

def main():
    dev = MIC_DEVICE_INDEX
    print("Input-Device:", dev)
    with sd.InputStream(channels=1, dtype="float32", callback=lambda *a, **k: None, device=dev):
        print("Starte Pegeltest (3s)… sprich ins Mikro.")
        t0 = time.time()
        rms = 0.0
        def cb(indata, frames, time_info, status):
            nonlocal rms
            if status: print("Status:", status)
            rms = np.sqrt(np.mean(indata**2))
        with sd.InputStream(channels=1, dtype="float32", callback=cb, device=dev):
            while time.time() - t0 < 3:
                bar = int(min(40, rms*200))
                print("[" + "#"*bar + " "*(40-bar) + "]", end="\r")
                time.sleep(0.05)
        print("\nFertig.")
if __name__ == "__main__":
    main()