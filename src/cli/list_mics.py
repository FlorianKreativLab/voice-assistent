# src/cli/list_mics.py
import sounddevice as sd
for i, dev in enumerate(sd.query_devices()):
    if dev["max_input_channels"] > 0:
        print(f"[{i}] {dev['name']}  (rate max: {dev['default_samplerate']})")
