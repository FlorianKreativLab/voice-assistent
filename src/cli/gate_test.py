from ..speech.tts.engine import speak
from ..audio.gate import is_speaking
import time

def main():
    print("SPEAKING vor TTS:", is_speaking())
    speak("Das ist ein Test. Während ich spreche, sollte das Mikro stumm sein.", voice_hint="Anna")
    print("SPEAKING direkt nach TTS:", is_speaking())
    time.sleep(0.5)
    print("SPEAKING nach 0.5s:", is_speaking())

if __name__ == "__main__":
    main()
