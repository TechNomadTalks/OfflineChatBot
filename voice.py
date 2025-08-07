import pyttsx3
import threading
import queue
import time
from utils.memory import recall_memory  # updated import

class VoiceSystem:
    def __init__(self):
        self.engine = None
        self.voice_queue = queue.Queue()
        self.active = False
        self.thread = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize TTS engine with preferred voices and start consumer thread."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            self.engine.setProperty('volume', 0.9)

            preferred_voices = [
                'Microsoft David',
                'Zira',
                'TTS_MS_EN-US_DAVID_11.0',
                'english'
            ]

            voices = self.engine.getProperty('voices')
            for voice in voices:
                if any(v.lower() in voice.name.lower() for v in preferred_voices):
                    self.engine.setProperty('voice', voice.id)
                    break

            self.active = True
            self._start_consumer_thread()

        except Exception as e:
            print(f"Voice init error: {e}")
            self.active = False

    def _start_consumer_thread(self):
        """Background thread consumes queued texts to speak."""
        def consumer():
            while self.active:
                try:
                    text = self.voice_queue.get(timeout=1)
                    if text is None:  # shutdown signal
                        break
                    self._safe_speak(text)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Voice error: {e}")

        self.thread = threading.Thread(target=consumer, daemon=True)
        self.thread.start()

    def _safe_speak(self, text: str):
        """Attempt speaking with retries."""
        for attempt in range(3):
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                print(f"Speech attempt {attempt + 1} failed: {e}")
                time.sleep(0.5)
        print("Voice system unavailable after retries")

    def speak(self, text: str) -> bool:
        """Queue text for speech; returns False if system inactive."""
        if not self.active:
            # Do NOT print every time speak is called to avoid duplication
            return False
        try:
            self.voice_queue.put(text)
            return True
        except Exception as e:
            print(f"Queue error: {e}")
            return False

    def shutdown(self):
        """Stop thread and engine."""
        self.active = False
        if self.thread:
            self.voice_queue.put(None)  # Signal shutdown
            self.thread.join(timeout=2)
        if self.engine:
            self.engine.stop()
            del self.engine

# Singleton instance
voice_system = VoiceSystem()

# Public interface
def speak(text: str) -> bool:
    return voice_system.speak(text)

def voice_available() -> bool:
    return voice_system.active
