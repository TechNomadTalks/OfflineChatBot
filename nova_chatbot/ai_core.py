"""
AI core - handles switching between online and offline AI models.
"""

from .config import config
from .online_ai import get_online_response
from .local_ai import local_ai


# Default to offline mode (local AI)
CURRENT_AI_MODE = 'phi-3'


def get_ai_response(prompt, chat_history=None):
    """
    Get a response from the current AI model.
    
    Args:
        prompt: The user's input
        chat_history: List of previous conversation entries
    
    Returns:
        Tuple of (response_text, elapsed_time)
    """
    # Check if we should use online or offline mode
    if config.is_offline_mode():
        return local_ai.generate_local_response(prompt, chat_history or [])
    
    # Check for API key before trying online mode
    api_key = config.get_openai_api_key()
    if not api_key:
        # Fall back to local AI if no API key
        print("⚠️ No OpenAI API key found. Falling back to local AI (Ollama).")
        return local_ai.generate_local_response(prompt, chat_history or [])
    
    # Use online AI
    model = config.get_ai_model()
    return get_online_response(prompt, model)


def switch_ai_mode(mode):
    """
    Switch between AI modes.
    
    Args:
        mode: 'gpt-4o', 'gpt-4o-mini', 'phi-3', or other supported models
    """
    global CURRENT_AI_MODE
    
    if mode.startswith('gpt'):
        # Online mode
        CURRENT_AI_MODE = mode
    else:
        # Offline mode (local)
        CURRENT_AI_MODE = 'phi-3'


def get_current_mode():
    """Get the current AI mode."""
    if config.is_offline_mode():
        return "offline"
    return f"online ({config.get_ai_model()})"
