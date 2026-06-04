"""
AI core - handles switching between online and offline AI models.
"""

from .config import config
from .online_ai import get_online_response
from .local_ai import local_ai


CURRENT_AI_MODE = 'glm-5.1'
TOKEN_LIMITS = {
    'glm-5.1': 128000,
    'gpt-4o': 128000,
    'gpt-4o-mini': 128000,
    'phi-3': 4096,
}


def count_tokens(text, model='glm-5.1'):
    """Count tokens in text using tiktoken."""
    try:
        import tiktoken
    except ImportError:
        return 0
    try:
        enc = tiktoken.encoding_for_model(model)
    except KeyError:
        enc = tiktoken.get_encoding('cl100k_base')
    return len(enc.encode(text))


def trim_history(history, model='glm-5.1', reserve_ratio=0.2):
    """Trim conversation history to fit within token limit."""
    if not history:
        return []
    
    token_limit = TOKEN_LIMITS.get(model, 4096)
    max_tokens = int(token_limit * (1 - reserve_ratio))
    
    total_tokens = 0
    trimmed = []
    for entry in reversed(history):
        entry_text = f"User: {entry.get('user', '')} Bot: {entry.get('bot', '')}"
        entry_tokens = count_tokens(entry_text, model)
        if total_tokens + entry_tokens > max_tokens:
            break
        total_tokens += entry_tokens
        trimmed.insert(0, entry)
    
    return trimmed


def get_ai_response(prompt, chat_history=None):
    """
    Get a response from the current AI model.
    
    Args:
        prompt: The user's input
        chat_history: List of previous conversation entries
    
    Returns:
        Tuple of (response_text, elapsed_time)
    """
    if config.is_offline_mode():
        return local_ai.generate_local_response(prompt, chat_history or [])
    
    api_key = config.get_zai_api_key()
    if not api_key:
        api_key = config.get_openai_api_key_fallback()
        if not api_key:
            print("[WARN] No API key found. Falling back to local AI (Ollama).")
            return local_ai.generate_local_response(prompt, chat_history or [])
    
    model = config.get_ai_model()
    return get_online_response(prompt, model)


def switch_ai_mode(mode):
    """
    Switch between AI modes.
    
    Args:
        mode: 'gpt-4o', 'gpt-4o-mini', 'glm-5.1', 'phi-3', or other supported models
    """
    global CURRENT_AI_MODE
    
    if mode.startswith('gpt') or mode == 'glm-5.1':
        CURRENT_AI_MODE = mode
    else:
        CURRENT_AI_MODE = 'phi-3'


def get_current_mode():
    """Get the current AI mode."""
    if config.is_offline_mode():
        return "offline"
    return f"online ({config.get_ai_model()})"
