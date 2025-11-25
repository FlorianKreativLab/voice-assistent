# src/cli/ollama_test.py
import requests, json

def main():
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2:1b",   # oder mistral:7b, wenn du das hast
        "prompt": "Sag Hallo, ich stehe dir zu diensten. Was kann ich für sie erledigen mein Gebieter!"
    }

    print("👉 Sende an Ollama…")
    with requests.post(url, json=payload, stream=True) as r:
        r.raise_for_status()
        for line in r.iter_lines(decode_unicode=True):
            if line:
                try:
                    data = json.loads(line)
                    token = data.get("response")
                    if token:
                        print(token, end="", flush=True)
                except json.JSONDecodeError:
                    continue
    print("\n✅ Fertig.")

if __name__ == "__main__":
    main()