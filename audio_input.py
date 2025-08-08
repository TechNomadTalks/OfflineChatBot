import os
import queue
import sounddevice as sd
import vosk
import json
import threading

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-en-us-0.42-gigaspeech"))

class SpeechRecognizer:
    def __init__(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Vosk model not found at {MODEL_PATH}")
        self.model = vosk.Model(MODEL_PATH)
        self.q = queue.Queue()
        self.running = False
        self.result = None
        self.thread = None

    def callback(self, indata, frames, time, status):
        if status:
            print(f"Audio status: {status}", flush=True)
        self.q.put(bytes(indata))

    def start_listening(self):
        if self.running:
            return
        self.running = True
        self.rec = vosk.KaldiRecognizer(self.model, 16000)
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        with sd.RawInputStream(samplerate=16000, blocksize=8000, dtype='int16',
                               channels=1, callback=self.callback):
            print("Listening... Say something!")
            while self.running:
                data = self.q.get()
                if self.rec.AcceptWaveform(data):
                    res = json.loads(self.rec.Result())
                    text = res.get("text", "")
                    if text:
                        self.result = text
                        print(f"Recognized: {text}")
                else:
                    # Partial result if needed:
                    pass

    def get_result(self):
        text = self.result
        self.result = None  # reset after read
        return text

    def stop_listening(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)

speech_recognizer = SpeechRecognizer()

def start_voice_input():
    speech_recognizer.start_listening()

def get_voice_text():
    return speech_recognizer.get_result()

def stop_voice_input():
    speech_recognizer.stop_listening()
