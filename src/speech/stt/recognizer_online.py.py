# src/speech/stt/recognizer_online.py
from .config import DEFAULT_SECONDS
def transcribe_online(seconds: int | None = None, language: str = "de-DE") -> str:
    """
    Online-STT mit SpeechRecognition (Google-Backend).
    Braucht Internet UND meist PyAudio für Mikrofon.
    """
    seconds = seconds or DEFAULT_SECONDS
    try:
        import speech_recognition as sr
    except Exception as e:
        print("❌ SpeechRecognition nicht installiert:", e)
        return ""

    r = sr.Recognizer()

    # Teste, ob PyAudio da ist (wird für Mikro benötigt)
    try:
        import pyaudio  # noqa: F401
    except Exception:
        print("⚠️  PyAudio fehlt – Online-STT per Mikro nicht möglich.")
        print("    Installier es (pip install pyaudio) oder nutze offline (Vosk).")
        return ""

    # Wenn wir bis hier kommen, versuchen wir Mikro-Aufnahme
    try:
        with sr.Microphone() as source:
            print(f"🎤 (ONLINE) Bitte sprich jetzt (max {seconds}s)...")
            audio = r.listen(source, timeout=seconds, phrase_time_limit=seconds)
        try:
            text = r.recognize_google(audio, language=language)
            return text
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            print("❌ Online-Anfrage fehlgeschlagen:", e)
            return ""
    except Exception as e:
        print("❌ Mikrofon-Zugriff (online) fehlgeschlagen:", e)
        return ""