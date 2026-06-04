"""
Text-to-speech module with ElevenLabs primary and pyttsx3 fallback.
"""

import os
from .config import config

try:
    from elevenlabs import generate, play, VoiceSettings
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False


VOICE_PRESETS = {
    'jarvis': {'voice_id': 'pMsXgV2OhLO1IsvrKWfX', 'stability': 0.4, 'similarity_boost': 0.8},
    'nova': {'voice_id': 'pMsXgV2OhLO1IsvrKWfX', 'stability': 0.5, 'similarity_boost': 0.5},
    'casual': {'voice_id': 'EXAVITQu4vr4xnSDxMaL', 'stability': 0.7, 'similarity_boost': 0.6},
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


def create_tts_provider():
    """Create the appropriate TTS provider based on config."""
    provider = config.get_tts_provider()
    profile = config.get_personality_profile()
    
    if provider == 'elevenlabs':
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
    return tts_provider.speak(text)


def is_available() -> bool:
    """Check if TTS is available."""
    return hasattr(tts_provider, 'engine') or ELEVENLABS_AVAILABLE