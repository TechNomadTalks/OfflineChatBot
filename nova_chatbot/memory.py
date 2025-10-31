import os
import json

MEMORY_FILE = os.path.join(os.path.dirname(__file__), "..", "memory.json")
MEMORY_FILE = os.path.abspath(MEMORY_FILE)

def recall_memory():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("⚠️ Warning: memory.json does not contain a list. Resetting memory.")
                return []
    except json.JSONDecodeError:
        print("⚠️ Warning: memory.json is corrupted or invalid JSON. Resetting memory.")
        return []

def store_memory(prompt, response):
    history = recall_memory()

    if not isinstance(history, list):
        history = []

    history.append({"user": prompt, "bot": response})

    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history[-50:], f, indent=2)
