# src/cli/talk_chat_stream.py
import time, traceback

from ..speech.wake.detector import listen_for_wake, WINDOW_SEC
from ..speech.stt.recognizer_vosk_inline import transcribe_until_silence
from ..speech.tts.engine import speak
from ..llm.ollama_client import OllamaChat
from ..llm.memory import ChatMemory

VOICE_NAME     = "Anna"
POST_TTS_PAUSE = 0.3
LLM_TIMEOUT_S  = 20.0
EMPTY_TURNS_EXIT = 2

VAD_MAX_SECONDS = 8.0
VAD_SILENCE_MS  = 600
VAD_RMS_THRESH  = 0.012

END_WORDS   = {"stopp", "stop", "ende", "beenden", "tschüss", "fertig"}
RESET_WORDS = {"reset", "neustart", "vergiss das"}

HELP_TEXT = (
    "Sag 'Heidi', dann deine Frage. "
    "Während ich antworte, rede ich Satz für Satz. "
    "Sag 'stopp' zum Beenden oder 'reset' für Neustart."
)

def _sentences(text):
    buf = []
    for ch in text:
        buf.append(ch)
        if ch in ".!?":
            yield "".join(buf).strip()
            buf = []
    if buf:
        yield "".join(buf).strip()

def main():
    brain  = OllamaChat(timeout_s=LLM_TIMEOUT_S)
    memory = ChatMemory(max_turns=6)

    print("[INFO] gestartet. " + HELP_TEXT)
    speak("Bereit. " + HELP_TEXT, voice_hint=VOICE_NAME, rate=185)

    in_dialog = False
    empty_count = 0

    try:
        while True:
            if not in_dialog:
                print("[STATE] warte auf Wake…")
                if not listen_for_wake(seconds=WINDOW_SEC):
                    time.sleep(0.05); continue
                speak("Ja, bitte?", voice_hint=VOICE_NAME, rate=190)
                time.sleep(POST_TTS_PAUSE)
                in_dialog, empty_count = True, 0
                continue

            print("[STT] höre bis Stille…")
            try:
                user_text = transcribe_until_silence(
                    max_seconds=VAD_MAX_SECONDS,
                    silence_ms=VAD_SILENCE_MS,
                    rms_threshold=VAD_RMS_THRESH
                )
            except Exception:
                print("[STT:ERROR]\n", traceback.format_exc())
                user_text = ""

            user_text = (user_text or "").strip()
            print("[STT] erkannt:", repr(user_text))

            if not user_text:
                empty_count += 1
                if empty_count >= EMPTY_TURNS_EXIT:
                    speak("Ich warte wieder auf Heidi.", voice_hint=VOICE_NAME)
                    in_dialog = False
                continue

            empty_count = 0
            low = user_text.lower()

            if low in END_WORDS:
                speak("Okay, bis bald!", voice_hint=VOICE_NAME); break
            if low in RESET_WORDS:
                memory.clear()
                speak("Verlauf gelöscht.", voice_hint=VOICE_NAME); continue

            memory.add_user(user_text)
            hist = memory.messages
            print("[LLM] starte Streaming…")

            try:
                stream = brain.chat_stream(hist)
            except Exception:
                print("[LLM:ERROR]\n", traceback.format_exc())
                speak("Fehler bei der Antwort.", voice_hint=VOICE_NAME)
                continue

            buffer, last_speak = [], time.time()
            for token in stream:
                print(token, end="", flush=True)
                buffer.append(token)

                join_txt = "".join(buffer)
                if any(join_txt.endswith(x) for x in ".!?"):
                    for s in _sentences(join_txt):
                        speak(s, voice_hint=VOICE_NAME, rate=185)
                    buffer.clear()
                    last_speak = time.time()

                elif (time.time() - last_speak > 2.0) and len(join_txt) > 30:
                    # falls länger kein Satzende kam, trotzdem sprechen
                    speak(join_txt.strip(), voice_hint=VOICE_NAME, rate=185)
                    buffer.clear()
                    last_speak = time.time()

            # Reste ausgeben
            remaining = "".join(buffer).strip()
            if remaining:
                speak(remaining, voice_hint=VOICE_NAME, rate=185)

            print()
            memory.add_assistant(" ".join(memory.messages[-1].values()))  # grob anhängen
            time.sleep(POST_TTS_PAUSE)

    except KeyboardInterrupt:
        print("\n[INFO] beendet.")
