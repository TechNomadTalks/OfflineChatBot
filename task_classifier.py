# Plugin: task_classifier.py
# Classifies the user's input into categories like coding, recipe, general help, etc.

def run(user_input=None):
    return "Plugin 'task_classifier' requires input via on_message."

def on_message(message, online_mode=False):
    keywords = {
        "coding": ["code", "program", "python", "javascript", "debug", "compile"],
        "recipe": ["recipe", "cook", "ingredient", "bake", "meal", "kitchen"],
        "general": ["help", "assist", "support", "question"],
        "windows": ["open", "launch", "start", "run"],
        "search": ["google", "search", "lookup", "find", "look up"],
    }

    message_lower = message.lower()
    for category, keys in keywords.items():
        if any(k in message_lower for k in keys):
            return f"[Task Classifier] Detected category: {category.capitalize()}"

    return None
