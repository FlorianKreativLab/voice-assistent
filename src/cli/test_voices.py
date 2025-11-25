# src/cli/test_voices.py
import platform
import subprocess

def test_macos_say_voices(sample_text="Hallo, ich bin Bobby Junior!"):
    if platform.system() != "Darwin":
        print("Dieses Tool funktioniert nur auf macOS.")
        return
    try:
        # Alle Stimmen abfragen
        out = subprocess.check_output(["say", "-v", "?"], text=True)
        lines = out.strip().splitlines()
        for line in lines:
            parts = line.split()
            if not parts:
                continue
            voice_name = parts[0]
            print(f"--> Teste Stimme: {voice_name}")
            try:
                subprocess.run(["say", "-v", voice_name, sample_text])
            except Exception as e:
                print("   Fehler:", e)
    except Exception as e:
        print("Fehler beim Abfragen:", e)

if __name__ == "__main__":
    test_macos_say_voices()