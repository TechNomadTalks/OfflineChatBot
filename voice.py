import pyttsx3
import threading
import queue
import time

class VoiceSystem:
    def __init__(self):
        self.engine = None
        self.voice_queue = queue.Queue()
        self.active = False
        self.thread = None
        self._initialize_engine()

    def _initialize_engine(self):
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
        def consumer():
            while self.active:
                try:
                    text = self.voice_queue.get(timeout=1)
                    if text is None:
                        break
                    self._safe_speak(text)
                except queue.Empty:
                    continue
                except Exception as e:
                    print(f"Voice error: {e}")
        self.thread = threading.Thread(target=consumer, daemon=True)
        self.thread.start()

    def _safe_speak(self, text: str):
        for attempt in range(3):
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                print(f"Speech attempt {attempt + 1} failed: {e}")
                time.sleep(0.5)
                if attempt == 2:
                    print("Voice system unavailable")

    def speak(self, text: str) -> bool:
        if not self.active:
            print("Voice system not initialized")
            return False
        try:
            self.voice_queue.put(text)
            return True
        except Exception as e:
            print(f"Queue error: {e}")
            return False

    def shutdown(self):
        self.active = False
        if self.thread:
            self.voice_queue.put(None)
            self.thread.join(timeout=2)
        if self.engine:
            self.engine.stop()
            del self.engine

voice_system = VoiceSystem()

def speak(text: str) -> bool:
    return voice_system.speak(text)

def voice_available() -> bool:
    return voice_system.active
