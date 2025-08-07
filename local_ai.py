import requests
import time
from typing import List, Dict, Tuple, Optional

class LocalAI:
    def __init__(self, model_name: str = "phi", base_url: str = "http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = 30

    def generate_response(self, prompt: str, chat_history: Optional[List[Dict]] = None) -> Tuple[str, float]:
        # chat_history currently unused but included for interface consistency
        start_time = time.time()
        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "No response from local AI.")
            return text.strip(), round(time.time() - start_time, 2)
        except requests.exceptions.RequestException as e:
            return f"Local AI error: {e}", round(time.time() - start_time, 2)

# Singleton instance for use in main.py
local_ai = LocalAI()