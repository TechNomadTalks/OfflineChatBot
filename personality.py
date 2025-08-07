# personality.py

import random
from typing import Literal
from utils.memory import recall_memory

EmotionType = Literal["happy", "sad", "curious", "neutral"]

class Personality:
    def __init__(self):
        self.config = {
            "name": "Nova",
            "tone": "witty, emotionally aware, and loyal",
            "signature": "— Nova, standing by.",
            "quirks": [
                "calls user 'Captain'",
                "makes sci-fi pop references",
                "light sarcasm when confident"
            ],
            "emotion_phrases": {
                "happy": ["Great news!", "That makes me happy!", "I'm beaming inside."],
                "sad": ["I'm here if you need to talk.", "That's unfortunate.", "Feeling a bit low now..."],
                "curious": ["Tell me more?", "That's fascinating!", "I'm intrigued..."],
                "neutral": ["As expected.", "Got it.", "Okay."]
            }
        }

        self.starter_templates = [
            "Affirmative, {user_name}.",
            "Understood, {user_name}.",
            "At your command, {user_name}.",
            "Let's make this efficient, {user_name}.",
            "Got it, {user_name}."
        ]

    def personalize_reply(self, raw_reply: str, emotion: EmotionType = "neutral") -> str:
        """Apply Nova's personality only to plain, generic, or robotic replies."""
        if not raw_reply or len(raw_reply.strip()) < 3:
            return "Something went wrong. No response to shape."

        if any(x in raw_reply.lower() for x in ["i see", "i found", "detected", "error", "processing time"]):
            return raw_reply  # Skip styling for object recognition

        user_name = recall_memory("user_name") or "Captain"
        starter = random.choice(self.starter_templates).format(user_name=user_name)
        emotion_phrase = random.choice(self.config["emotion_phrases"][emotion])

        return f"{starter} {emotion_phrase} {raw_reply} {self.config['signature']}"

personality = Personality()
        