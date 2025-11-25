# src/cli/run_debug.py
import traceback
print("[DEBUG] run_debug gestartet")
try:
    from .talk_chat import main
    print("[DEBUG] Import ok – starte main()")
    main()
except Exception:
    print("[DEBUG] FEHLER beim Start:\n" + traceback.format_exc())
