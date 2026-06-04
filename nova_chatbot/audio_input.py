import os
import queue
import json
import threading

MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "models", "vosk-model-en-us-0.42-gigaspeech"))
_model_loaded = False
_model_error = None

def _load_model():
    global _model_loaded, _model_error, model, q, running, result, thread
    
    if not os.path.exists(MODEL_PATH):
        _model_error = f"Vosk model not found at {MODEL_PATH}. Download from https://alphacephei.com/vosk/models"
        return False
    
    try:
        import sounddevice as sd
        import vosk
        model = vosk.Model(MODEL_PATH)
        q = queue.Queue()
        running = False
        result = None
        thread = None
        _model_loaded = True
        return True
    except ImportError as e:
        _model_error = f"Required package not installed: {e}"
        return False
    except Exception as e:
        _model_error = f"Failed to load model: {e}"
        return False


class SpeechRecognizer:
    def __init__(self):
        if not _load_model():
            raise FileNotFoundError(_model_error or "Vosk model not initialized")
        self.model = model
        self.q = q
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
        import sounddevice as sd
        import vosk
        self.rec = vosk.KaldiRecognizer(self.model, 16000)
        self.thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.thread.start()

    def _listen_loop(self):
        import sounddevice as sd
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

    def get_result(self):
        text = self.result
        self.result = None
        return text

    def stop_listening(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)


speech_recognizer = None


def _get_recognizer():
    global speech_recognizer
    if speech_recognizer is None:
        if not _load_model():
            raise FileNotFoundError(_model_error or "Vosk model not initialized")
        speech_recognizer = SpeechRecognizer()
    return speech_recognizer


def start_voice_input():
    _get_recognizer().start_listening()


def get_voice_text():
    return speech_recognizer.get_result() if speech_recognizer else ""


def stop_voice_input():
    if speech_recognizer:
        speech_recognizer.stop_listening()
