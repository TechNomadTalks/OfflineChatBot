import threading
import time
import random
from .voice import speak

class ProactiveMessenger(threading.Thread):
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
        ]

    def run(self):
        while self._running:
            time.sleep(random.randint(60, 300))
            if self._running:
                message = random.choice(self.messages)
                print(f"\n[Nova]: {message}")
                speak(message)

    def stop(self):
        self._running = False
