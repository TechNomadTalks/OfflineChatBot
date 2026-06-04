"""
Simple JSON-based conversation memory.
"""

import os
import json
from .config import config


def get_memory_file_path():
    """Get the path to the memory file."""
    # Try to find memory.json in the project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    memory_path = os.path.join(base_dir, "memory.json")
    return memory_path


def recall_memory(query=None):
    """
    Load conversation history from memory file.
    
    Args:
        query: Optional query string (ignored for JSON memory, included for API compatibility)
    
    Returns:
        List of conversation entries, each with 'user' and 'bot' keys
    """
    memory_path = get_memory_file_path()
    
    if not os.path.exists(memory_path):
        return []

    try:
        with open(memory_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print("⚠️ Warning: memory.json does not contain a list. Resetting memory.")
                return []
    except json.JSONDecodeError:
        print("⚠️ Warning: memory.json is corrupted or invalid JSON. Resetting memory.")
        return []
    except Exception as e:
        print(f"⚠️ Error reading memory: {e}")
        return []


def store_memory(prompt, response):
    """
    Store a conversation entry in memory.
    
    Args:
        prompt: The user's message
        response: The bot's response
    """
    history = recall_memory()

    if not isinstance(history, list):
        history = []

    history.append({"user": prompt, "bot": response})
    
    # Get max entries from config
    max_entries = config.get_memory_max_entries()
    
    # Keep only the last N entries
    history = history[-max_entries:]
    
    memory_path = get_memory_file_path()
    with open(memory_path, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)


def clear_memory():
    """Clear all conversation history."""
    memory_path = get_memory_file_path()
    if os.path.exists(memory_path):
        os.remove(memory_path)


def export_memory(filepath):
    """Export conversation history to a file."""
    history = recall_memory()
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2)
        return True, f"Exported {len(history)} entries to {filepath}"
    except Exception as e:
        return False, f"Export failed: {e}"


def import_memory(filepath):
    """Import conversation history from a file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            return False, "Invalid format: expected a list"
        
        existing = recall_memory()
        combined = existing + data
        max_entries = config.get_memory_max_entries()
        combined = combined[-max_entries:]
        
        memory_path = get_memory_file_path()
        with open(memory_path, 'w', encoding='utf-8') as f:
            json.dump(combined, f, indent=2)
        return True, f"Imported {len(data)} entries from {filepath}"
    except FileNotFoundError:
        return False, f"File not found: {filepath}"
    except Exception as e:
        return False, f"Import failed: {e}"


def search_memory(query):
    """Search memory for entries containing query."""
    history = recall_memory()
    results = []
    query_lower = query.lower()
    for entry in history:
        if query_lower in entry.get('user', '').lower() or query_lower in entry.get('bot', '').lower():
            results.append(entry)
    return results
