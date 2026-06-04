import os
import configparser


class Config:
    """Configuration manager for Nova Chatbot."""
    
    # Placeholder values that indicate the user needs to set up the config
    PLACEHOLDER_PREFIXES = ['your_', 'placeholder', 'replace_me', 'change_me']
    
    def __init__(self, file_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(file_path)
        
        # Determine base directory (support both running from repo root and from nova_chatbot)
        if os.path.exists(file_path):
            self.base_dir = os.path.dirname(os.path.abspath(file_path))
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

    def get(self, section, key, default=None):
        """Get a configuration value."""
        return self.config.get(section, key, fallback=default)

    def get_boolean(self, section, key, default=False):
        """Get a boolean configuration value."""
        value = self.get(section, key, str(default))
        return value.lower() in ('true', '1', 'yes', 'on')

    def get_int(self, section, key, default=0):
        """Get an integer configuration value."""
        try:
            return int(self.get(section, key, str(default)))
        except ValueError:
            return default

    def get_openai_api_key(self):
        """Get OpenAI API key with validation."""
        key = self.get('api_keys', 'openai')
        if key and self._is_placeholder(key):
            return None
        return key

    def get_elevenlabs_api_key(self):
        """Get ElevenLabs API key with validation."""
        key = self.get('api_keys', 'elevenlabs')
        if key and self._is_placeholder(key):
            return None
        return key

    def get_zai_api_key(self):
        """Get Z.AI API key with validation."""
        key = self.get('api_keys', 'zai')
        if key and self._is_placeholder(key):
            return None
        return key

    def get_openai_api_key_fallback(self):
        """Get OpenAI API key as fallback."""
        key = self.get('api_keys', 'openai')
        if key and self._is_placeholder(key):
            return None
        return key

    def get_tts_provider(self):
        """Get TTS provider (elevenlabs or pyttsx3)."""
        return self.get('tts', 'provider', 'pyttsx3')

    def get_elevenlabs_voice_id(self):
        """Get ElevenLabs voice ID."""
        return self.get('tts', 'voice_id', 'pMsXgV2OhLO1IsvrKWfX')

    def get_elevenlabs_stability(self):
        """Get ElevenLabs stability setting."""
        return float(self.get('tts', 'stability', '0.5'))

    def get_elevenlabs_similarity_boost(self):
        """Get ElevenLabs similarity boost setting."""
        return float(self.get('tts', 'similarity_boost', '0.5'))

    def get_personality_profile(self):
        """Get personality profile."""
        return self.get('personality', 'profile', 'jarvis')

    def get_temperature(self):
        """Get AI temperature."""
        return float(self.get('personality', 'temperature', '0.7'))

    def _is_placeholder(self, value):
        """Check if a value is a placeholder that needs to be replaced."""
        if not value:
            return True
        value_lower = value.lower()
        return any(value_lower.startswith(prefix) for prefix in self.PLACEHOLDER_PREFIXES)

    def is_offline_mode(self):
        """Check if offline mode is enabled."""
        return self.get_boolean('ai', 'offline_mode', True)

    def get_ai_model(self):
        """Get the AI model to use."""
        return self.get('ai', 'model', 'phi-3')

    def is_voice_enabled(self):
        """Check if voice output is enabled."""
        return self.get_boolean('voice', 'enabled', True)

    def is_memory_enabled(self):
        """Check if memory is enabled."""
        return self.get_boolean('memory', 'enabled', True)

    def get_memory_max_entries(self):
        """Get maximum memory entries."""
        return int(self.get('memory', 'max_entries', 50))

    def is_proactive_enabled(self):
        """Check if proactive messaging is enabled."""
        return self.get_boolean('proactive', 'enabled', True)

    def get_model_path(self):
        """Get the path to the YOLO model."""
        model_name = self.get('object_recognition', 'model', 'yolov8n.pt')
        # Check relative to base dir first, then relative to nova_chatbot
        for base in [self.base_dir, os.path.dirname(__file__)]:
            path = os.path.join(base, model_name)
            if os.path.exists(path):
                return path
        return os.path.join(os.path.dirname(__file__), '..', model_name)


# Create a default config object
config = Config()
