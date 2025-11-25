# src/audio/gate.py
import threading, time

_SPEAKING = False
_MUTE_UNTIL = 0.0
_LOCK = threading.Lock()

def set_speaking(flag: bool):
    global _SPEAKING
    with _LOCK:
        _SPEAKING = flag

def is_speaking() -> bool:
    with _LOCK:
        return _SPEAKING

def mute_for(seconds: float):
    global _MUTE_UNTIL
    with _LOCK:
        _MUTE_UNTIL = max(_MUTE_UNTIL, time.time() + seconds)

def wake_is_muted() -> bool:
    with _LOCK:
        return time.time() < _MUTE_UNTIL

class speaking_guard:
    """Während TTS: speaking=True, Wake/STT stumm; danach kurze Nachhall-Sperre."""
    def __init__(self, hold_after_s: float = 1.0):
        self.hold_after_s = hold_after_s
    def __enter__(self):
        set_speaking(True)
        mute_for(self.hold_after_s)
    def __exit__(self, exc_type, exc, tb):
        set_speaking(False)
        mute_for(self.hold_after_s)