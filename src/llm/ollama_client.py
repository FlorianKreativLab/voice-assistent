# src/llm/ollama_client.py
import json, requests
from typing import List, Dict, Generator, Optional

DEFAULT_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL    = "llama3.2:1b"

class OllamaChat:
    def __init__(
        self,
        model: str = DEFAULT_MODEL,
        base_url: str = DEFAULT_BASE_URL,
        system_prompt: Optional[str]=None,
        timeout_s: float = 15.0,     # <— harter Timeout pro Request
    ):
        self.model = model
        self.base  = base_url
        self.timeout_s = timeout_s
        self.system_prompt = system_prompt or (
            "Du bist ein freundlicher Roboter-Assistent. "
            "Antworte kurz, klar und auf Deutsch."
        )

    def chat_stream(self, history_and_user: List[Dict[str,str]]) -> Generator[str, None, None]:
        url = f"{self.base}/api/chat"
        payload = {
            "model": self.model,
            "messages": [{"role":"system","content": self.system_prompt}] + history_and_user,
            "stream": True,
            "options": {"temperature": 0.3, "num_ctx": 2048}
        }
        try:
            with requests.post(url, json=payload, stream=True, timeout=self.timeout_s) as r:
                r.raise_for_status()
                for line in r.iter_lines(decode_unicode=True):
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    token = data.get("message", {}).get("content")
                    if token:
                        yield token
        except requests.exceptions.RequestException as e:
            print("[OLLAMA:ERROR]", e)
            return  # beendet den Generator

    def chat(self, history_and_user: List[Dict[str,str]], max_chars: int = 600) -> str:
        out, total = [], 0
        for token in self.chat_stream(history_and_user):
            out.append(token); total += len(token)
            if total >= max_chars:
                out.append(" …"); break
        return "".join(out).strip()