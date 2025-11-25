# src/cli/list_voices.py
import platform
import subprocess

def list_macos_say_voices():
    if platform.system() != "Darwin":
        print("Dieses Tool funktioniert nur auf macOS.")
        return
    try:
        # -v ? zeigt alle systemstimmen
        out = subprocess.check_output(["say", "-v", "?"], text=True)
        print(out)
    except Exception as e:
        print("Fehler beim Abfragen:", e)

if __name__ == "__main__":
    list_macos_say_voices()
