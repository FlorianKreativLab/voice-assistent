# src/cli/talk_chat.py
import time
import sys
import threading
import traceback

from ..speech.wake.detector import listen_for_wake, WINDOW_SEC
from ..speech.stt.recognizer_vosk_inline import transcribe_until_silence
from ..speech.tts.engine import speak
from ..llm.ollama_client import OllamaChat
from ..llm.memory import ChatMemory
from ..audio.gate import wake_is_muted

# ---------------- Einstellungen ----------------
VOICE_NAME         = "kerstin-low"
POST_TTS_PAUSE     = 0.4          # kurze Pause nach TTS, damit das Mikro nicht Annas Stimme aufnimmt
LLM_TIMEOUT_S      = 15.0         # harter Timeout pro LLM-Runde
EMPTY_TURNS_EXIT   = 5            # wenn der Nutzer 2x nichts sagt, zurück in den Wake-Modus

# VAD/Erkennungs-Feintuning
VAD_MAX_SECONDS    = 12.0         # Obergrenze pro Nutzerbeitrag (ganze Sätze)
VAD_SILENCE_MS     = 700          # 500 = schneller, 800–900 = schneidet weniger ab
VAD_RMS_THRESH     = 0.012        # 0.010–0.012 empfindlicher, 0.014–0.018 robuster gg. Rauschen

END_WORDS          = {"stopp", "stop", "ende", "beenden", "tschüss", "tschuess", "fertig"}
RESET_WORDS        = {"reset", "neustart", "vergiss das", "vergiss"}

HELP_TEXT = (
    "Sag 'Heidi', dann deine Frage. "
    
)

# ---------------- Not-Aus (q + Enter) ----------------
STOP_FLAG = False

def _watch_quit_key():
    """
    Lauscht im Hintergrund auf 'q' + Enter und setzt STOP_FLAG = True.
    """
    global STOP_FLAG
    try:
        for line in sys.stdin:
            if line.strip().lower() == "q":
                STOP_FLAG = True
                print("\n[INFO] Not-Aus (q) erkannt – beende…")
                break
    except Exception:
        pass

# ---------------- Hauptprogramm ----------------
def main():
    global STOP_FLAG
    STOP_FLAG = False

    brain  = OllamaChat(timeout_s=LLM_TIMEOUT_S)
    memory = ChatMemory(max_turns=6)

    # Not-Aus-Thread starten
    t = threading.Thread(target=_watch_quit_key, daemon=True)
    t.start()

    print("[INFO] gestartet. " + HELP_TEXT)
    try:
        speak("Bereit. " + HELP_TEXT, voice_hint=VOICE_NAME, rate=185)
    except Exception:
        print("[TTS:WARN] Start-Ansage konnte nicht gesprochen werden.")

    in_dialog = False
    empty_count = 0

    try:
        while True:
            if STOP_FLAG:
                break

            if not in_dialog:
                # ---- IDLE: auf Wake warten ----
                print("[STATE] warte auf Wake… (q + Enter = Not-Aus)")
                woke = listen_for_wake(seconds=WINDOW_SEC, show_debug=False)
                if STOP_FLAG:
                    break
                if not woke:
                    time.sleep(0.05)
                    continue

                print("[STATE] Wake erkannt → DIALOG-Modus")
                try:
                    speak("Ja, bitte?", voice_hint=VOICE_NAME, rate=190)
                except Exception:
                    print("[TTS:WARN] Wake-Antwort konnte nicht gesprochen werden.")
                time.sleep(POST_TTS_PAUSE)

                in_dialog = True
                empty_count = 0
                continue

            # ---- DIALOG: zuhören bis Stille, ohne erneutes Wake ----
            if STOP_FLAG:
                break

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

            if STOP_FLAG:
                break

            if not user_text:
                empty_count += 1
                if empty_count >= EMPTY_TURNS_EXIT:
                    try:
                        speak("Ich warte wieder auf Heidi.", voice_hint=VOICE_NAME, rate=180)
                    except Exception:
                        print("[TTS:WARN] Rückmeldung 'warte wieder' fehlgeschlagen.")
                    in_dialog = False
                    continue
                # einmal „nichts“ ist ok – bleib im Dialog
                continue

            # wenn Text kam, Zähler zurücksetzen
            empty_count = 0
            low = user_text.lower()

            # ---- Steuerwörter ----
            if low in END_WORDS:
                try:
                    speak("Okay, bis bald!", voice_hint=VOICE_NAME)
                except Exception:
                    print("[TTS:WARN] Abschieds-TTS fehlgeschlagen.")
                break

            if low in RESET_WORDS:
                memory.clear()
                try:
                    speak("Verlauf gelöscht. Was möchtest du wissen?", voice_hint=VOICE_NAME)
                except Exception:
                    print("[TTS:WARN] TTS für Verlauf gelöscht fehlgeschlagen.")
                time.sleep(POST_TTS_PAUSE)
                continue

            # ---- LLM mit Verlauf ----
            memory.add_user(user_text)
            hist = memory.messages
            print(f"[LLM] rufe Ollama… (Timeout {LLM_TIMEOUT_S}s)")
            try:
                answer = brain.chat(hist, max_chars=600)
            except Exception:
                print("[LLM:ERROR]\n", traceback.format_exc())
                answer = ""

            if STOP_FLAG:
                break

            if not answer:
                try:
                    speak("Ich habe gerade keine Antwort bekommen.", voice_hint=VOICE_NAME)
                except Exception:
                    print("[TTS:WARN] TTS für 'keine Antwort' fehlgeschlagen.")
                time.sleep(0.3)
                continue

            print("[BOT]", answer)
            memory.add_assistant(answer)

            # ---- TTS der Antwort ----
            try:
                speak(answer, voice_hint=VOICE_NAME, rate=185)
            except Exception:
                print("[TTS:ERROR]\n", traceback.format_exc())

            time.sleep(POST_TTS_PAUSE)

    except KeyboardInterrupt:
        print("\n[INFO] beendet durch Nutzer (Strg+C).")
    finally:
        print("[INFO] Programmende.")

# Direkter Start
if __name__ == "__main__":
    main()