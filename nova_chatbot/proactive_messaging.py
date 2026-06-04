"""
Proactive messaging - Nova occasionally speaks up on her own.
"""

import threading
import time
import random
from .voice import speak
from .config import config
from .memory import recall_memory


class ProactiveMessenger(threading.Thread):
    """Background thread that occasionally sends proactive messages."""
    
    def __init__(self):
        super().__init__()
        self.daemon = True
        self._running = True
        self.messages = [
            "Just thinking...",
            "Did you know that the first computer bug was a real moth?",
            "I'm learning new things every day!",
            "I'm here if you need anything.",
            "What's on your mind?",
            "I was just reading about the history of AI. It's fascinating!",
            "I could help you with coding, file processing, or just chatting!",
            "The weather outside is... well, I don't actually know. I'm stuck in here!",
        ]
        self.min_interval = config.get_int('proactive', 'min_interval', 120)
        self.max_interval = config.get_int('proactive', 'max_interval', 300)
        self.max_memory_entries = config.get_int('proactive', 'max_memory_entries', 5)

    def run(self):
        """Main loop - periodically send messages."""
        while self._running:
            interval = random.randint(self.min_interval, self.max_interval)
            
            for _ in range(interval):
                if not self._running:
                    break
                time.sleep(1)
            
            if self._running and config.is_voice_enabled():
                memory = recall_memory()
                if memory and len(memory) > 3:
                    last_user = memory[-1].get('user', '')[:50] if memory else ''
                    message = f"I noticed you said '{last_user}' earlier. Everything still on your mind?"
                else:
                    message = random.choice(self.messages)
                
                print(f"\n[Nova]: {message}")
                speak(message)

    def stop(self):
        """Stop the proactive messenger."""
        self._running = False
