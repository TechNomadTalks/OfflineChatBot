import os
import configparser

class Config:
    def __init__(self, file_path='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(file_path)

    def get(self, section, key, default=None):
        return self.config.get(section, key, fallback=default)

    def get_openai_api_key(self):
        return self.get('api_keys', 'openai')

    def get_elevenlabs_api_key(self):
        return self.get('api_keys', 'elevenlabs')

# Create a default config object
config = Config()
