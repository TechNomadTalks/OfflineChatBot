"""
Local AI integration using Ollama.
"""

import requests
import time
from typing import List, Dict, Tuple, Optional


class LocalAI:
    """Ollama-based local AI."""
    
    def __init__(self, model_name: str = "phi-3", base_url: str = "http://localhost:11434/api/generate"):
        self.model_name = model_name
        self.base_url = base_url
        self.timeout = 120  # Increased timeout for larger models

    def generate_local_response(self, prompt: str, chat_history: Optional[List[Dict]] = None) -> Tuple[str, float]:
        """
        Generate a response using local Ollama API.
        
        Args:
            prompt: The user's input
            chat_history: Previous conversation for context
            
        Returns:
            Tuple of (response_text, elapsed_time)
        """
        start_time = time.time()
        
        # Build context from chat history
        context = ""
        if chat_history and len(chat_history) > 0:
            context = "Previous conversation:\n"
            for entry in chat_history[-5:]:  # Use last 5 entries
                if isinstance(entry, dict):
                    user_msg = entry.get('user', '')
                    bot_msg = entry.get('bot', entry.get('nova', ''))
                    if user_msg:
                        context += f"User: {user_msg}\n"
                    if bot_msg:
                        context += f"Nova: {bot_msg}\n"
            context += "\n"
        
        full_prompt = context + f"User: {prompt}\nNova:" if context else prompt

        try:
            response = requests.post(
                self.base_url,
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                    }
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            text = data.get("response", "No response from local AI.")
            return text.strip(), round(time.time() - start_time, 2)
            
        except requests.exceptions.ConnectionError:
            return "❌ Cannot connect to Ollama. Make sure Ollama is running (ollama serve)", round(time.time() - start_time, 2)
        except requests.exceptions.Timeout:
            return "❌ Request timed out. Try a smaller model or increase timeout.", round(time.time() - start_time, 2)
        except requests.exceptions.RequestException as e:
            return f"Local AI error: {e}", round(time.time() - start_time, 2)
        except Exception as e:
            return f"❌ Unexpected error: {e}", round(time.time() - start_time, 2)

    def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            return response.status_code == 200
        except Exception:
            return False


# Global instance
local_ai = LocalAI()
