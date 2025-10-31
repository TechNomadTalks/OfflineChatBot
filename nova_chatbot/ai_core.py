from .config import config
from .online_ai import get_online_response
from .local_ai import local_ai

CURRENT_AI_MODE = config.get('ai', 'model', 'local')

def get_ai_response(prompt, chat_history):
    if CURRENT_AI_MODE.startswith('gpt'):
        return get_online_response(prompt)
    elif CURRENT_AI_MODE == 'phi-3':
        return local_ai.generate_local_response(prompt, chat_history)
    else:
        # Default to local AI if model is not recognized
        return local_ai.generate_local_response(prompt, chat_history)

def switch_ai_mode(mode):
    global CURRENT_AI_MODE
    CURRENT_AI_MODE = mode
