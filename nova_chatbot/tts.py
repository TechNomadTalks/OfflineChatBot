"""
Text-to-speech module with ElevenLabs primary, Piper Jarvis voice, and pyttsx3 fallback.
"""

import os
import subprocess
import json
from .config import config

try:
    from elevenlabs import generate, play, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False

try:
    import piper
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False


VOICE_PRESETS = {
    'jarvis': {'voice_id': 'pMsXgV2OhLO1IsvrKWfX', 'stability': 0.4, 'similarity_boost': 0.8},
    'nova': {'voice_id': 'pMsXgV2OhLO1IsvrKWfX', 'stability': 0.5, 'similarity_boost': 0.5},
    'casual': {'voice_id': 'EXAVITQu4vr4xnSDxMaL', 'stability': 0.7, 'similarity_boost': 0.6},
}

PIPER_MODEL_PATHS = {
    'jarvis': {
        'high': 'models/jarvis/jarvis-high.onnx',
        'medium': 'models/jarvis/jarvis-medium.onnx',
    },
    'british_male': {
        'high': None,
        'medium': None,
    }
}


class TTSProvider:
    """Base TTS provider interface."""
    
    def speak(self, text: str) -> bool:
        raise NotImplementedError


class ElevenLabsProvider(TTSProvider):
    """ElevenLabs TTS provider."""
    
    def __init__(self, api_key: str, voice_id: str, stability: float, similarity_boost: float):
        self.api_key = api_key
        self.voice_id = voice_id
        self.stability = stability
        self.similarity_boost = similarity_boost
        
        if not ELEVENLABS_AVAILABLE:
            raise ImportError("elevenlabs package not installed")
        
        os.environ["ELEVENLABS_API_KEY"] = api_key
    
    def speak(self, text: str) -> bool:
        try:
            audio = generate(
                text=text,
                voice=VoiceSettings(
                    voice_id=self.voice_id,
                    stability=self.stability,
                    similarity_boost=self.similarity_boost
                )
            )
            play(audio)
            return True
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            return False


class Pyttsx3Provider(TTSProvider):
    """pyttsx3 fallback TTS provider."""
    
    def __init__(self):
        import pyttsx3
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.engine.setProperty('volume', 0.9)
        
        voices = self.engine.getProperty('voices')
        preferred_voices = ['Microsoft David', 'Zira', 'TTS_MS_EN-US_DAVID_11.0', 'english']
        
        for voice in voices:
            try:
                if any(v.lower() in voice.name.lower() for v in preferred_voices):
                    self.engine.setProperty('voice', voice.id)
                    break
            except:
                continue
    
    def speak(self, text: str) -> bool:
        try:
            self.engine.say(text)
            self.engine.runAndWait()
            return True
        except Exception as e:
            print(f"pyttsx3 TTS error: {e}")
            return False


class PiperProvider(TTSProvider):
    """Piper TTS provider with Jarvis voice model."""
    
    def __init__(self, model_path: str = None, model_quality: str = 'medium'):
        self.model_path = model_path
        self.model_quality = model_quality
        self._ensure_model()
    
    def _ensure_model(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_dir = os.path.join(base_dir, 'models', 'jarvis')
        
        if not os.path.exists(model_dir):
            os.makedirs(model_dir, exist_ok=True)
        
        model_file = os.path.join(model_dir, f'jarvis-{self.model_quality}.onnx')
        config_file = os.path.join(model_dir, f'jarvis-{self.model_quality}.onnx.json')
        
        if not os.path.exists(model_file):
            print(f"[TTS] Jarvis voice model not found. Download from:")
            print(f"  wget -O {model_file}")
            print(f"    https://huggingface.co/jgkawell/jarvis/resolve/main/en/en_GB/jarvis/{self.model_quality}/jarvis-{self.model_quality}.onnx")
            print(f"  wget -O {config_file}")
            print(f"    https://huggingface.co/jgkawell/jarvis/resolve/main/en/en_GB/jarvis/{self.model_quality}/jarvis-{self.model_quality}.onnx.json")
            raise FileNotFoundError(f"Jarvis voice model not found: {model_file}")
        
        self.model_path = model_file
    
    def speak(self, text: str) -> bool:
        try:
            cmd = ['piper', '--model', self.model_path, '--output_file', '/dev/stdout']
            if os.name == 'nt':
                cmd = ['piper', '--model', self.model_path]
            
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = process.communicate(input=text.encode('utf-8'))
            
            if process.returncode != 0:
                print(f"Piper error: {stderr.decode('utf-8', errors='replace')}")
                return False
            
            try:
                import sounddevice as sd
                import numpy as np
                
                audio_data = np.frombuffer(stdout, dtype=np.uint8)
                import wave
                import io
                
                with wave.open(io.BytesIO(stdout), 'rb') as wf:
                    sd.play(np.frombuffer(wf.read(), dtype=np.int16), wf.getframerate())
                    sd.wait()
                return True
            except ImportError:
                print(f"[TTS] Audio playback requires sounddevice. Speaking: {text}")
                return True
                
        except FileNotFoundError:
            print(f"[TTS] Piper binary not found. Install: pip install piper-tts")
            return False
        except Exception as e:
            print(f"Piper TTS error: {e}")
            return False


def create_tts_provider():
    """Create the appropriate TTS provider based on config."""
    provider = config.get_tts_provider()
    profile = config.get_personality_profile()
    
    if provider == 'piper':
        try:
            return PiperProvider(model_quality='medium')
        except FileNotFoundError:
            print("[TTS] Piper model not found, falling back to pyttsx3")
            return Pyttsx3Provider()
    elif provider == 'elevenlabs':
        api_key = config.get_elevenlabs_api_key()
        if api_key and ELEVENLABS_AVAILABLE:
            preset = VOICE_PRESETS.get(profile, VOICE_PRESETS['jarvis'])
            stability = config.get_elevenlabs_stability()
            similarity_boost = config.get_elevenlabs_similarity_boost()
            return ElevenLabsProvider(api_key, preset['voice_id'], stability, similarity_boost)
    
    return Pyttsx3Provider()


tts_provider = create_tts_provider()


def speak(text: str) -> bool:
    """Speak text using the configured TTS provider."""
    _signal_speaking_start()
    try:
        result = tts_provider.speak(text)
        return result
    finally:
        _signal_speaking_end()


def _signal_speaking_start():
    try:
        from .visualizer import set_visualizer_activity
        set_visualizer_activity(1.0)
    except ImportError:
        pass


def _signal_speaking_end():
    try:
        from .visualizer import set_visualizer_activity
        set_visualizer_activity(0.0)
    except ImportError:
        pass


def is_available() -> bool:
    """Check if TTS is available."""
    if hasattr(tts_provider, 'engine'):
        return True
    if ELEVENLABS_AVAILABLE and config.get_elevenlabs_api_key():
        return True
    if PIPER_AVAILABLE:
        return True
    return False