# src/llm/memory.py
from collections import deque
from typing import Deque, Dict, List

class ChatMemory:
    """
    Merkt sich die letzten N Nachrichten (User + Bot).
    """
    def __init__(self, max_turns: int = 6):
        self.max_turns = max_turns
        self._messages: Deque[Dict[str, str]] = deque()

    @property
    def messages(self) -> List[Dict[str, str]]:
        return list(self._messages)

    def add_user(self, text: str):
        self._messages.append({"role": "user", "content": text})
        self._trim()

    def add_assistant(self, text: str):
        self._messages.append({"role": "assistant", "content": text})
        self._trim()

    def clear(self):
        self._messages.clear()

    def _trim(self):
        # maximal 2 * max_turns Nachrichten (user+assistant pro Turn)
        while len(self._messages) > self.max_turns * 2:
            self._messages.popleft()
