"""
Voice output using pyttsx3 (Windows TTS).
"""

import pyttsx3
import threading
import queue
import time


class VoiceSystem:
    """Text-to-speech voice system."""
    
    def __init__(self):
        self.engine = None
        self.voice_queue = queue.Queue()
        self.active = False
        self.thread = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize the TTS engine."""
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 160)
            self.engine.setProperty('volume', 0.9)
            
            # Try to set a good voice
            voices = self.engine.getProperty('voices')
            
            # Preferred voices (in order of preference)
            preferred_voices = [
                'Microsoft David',
                'Zira',
                'TTS_MS_EN-US_DAVID_11.0',
                'english'
            ]
            
            for voice in voices:
                if any(v.lower() in voice.name.lower() for v in preferred_voices):
                    self.engine.setProperty('voice', voice.id)
                    break
            
            self.active = True
            self._start_consumer_thread()
            print("✅ Voice system initialized")
            
        except Exception as e:
            print(f"⚠️ Voice init error: {e}")
            self.active = False

    def _start_consumer_thread(self):
        """Start the background thread that processes voice queue."""
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
        """Safely speak text with retry logic."""
        for attempt in range(3):
            try:
                self.engine.say(text)
                self.engine.runAndWait()
                return
            except Exception as e:
                if attempt < 2:
                    time.sleep(0.5)
                else:
                    print(f"Voice system unavailable: {e}")

    def speak(self, text: str) -> bool:
        """Add text to the voice queue."""
        if not self.active:
            return False
        try:
            self.voice_queue.put(text)
            return True
        except Exception as e:
            print(f"Queue error: {e}")
            return False

    def shutdown(self):
        """Shutdown the voice system."""
        self.active = False
        if self.thread:
            try:
                self.voice_queue.put(None)
                self.thread.join(timeout=2)
            except Exception:
                pass
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass
            del self.engine
            self.engine = None


# Global instance
voice_system = VoiceSystem()


def speak(text: str) -> bool:
    """Speak text through the voice system."""
    return voice_system.speak(text)


def voice_available() -> bool:
    """Check if voice is available."""
    return voice_system.active
