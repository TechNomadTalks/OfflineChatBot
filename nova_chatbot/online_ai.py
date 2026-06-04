"""
Online AI integration using Z.AI GLM-5.1 (OpenAI-compatible API).
"""

import time
import openai
from .config import config
from .user_profile import format_user_context


def get_online_response(prompt: str, model: str = None) -> tuple[str, float]:
    """
    Get a response from Z.AI GLM-5.1 API.
    
    Args:
        prompt: The user's prompt
        model: The model to use (default: from config)
    
    Returns:
        Tuple of (response_text, elapsed_time)
    """
    start_time = time.time()
    full_response = ""
    
    api_key = config.get_zai_api_key()
    if not api_key:
        api_key = config.get_openai_api_key_fallback()
        if not api_key:
            # DEV/TEST FALLBACK - don't crash, just return help text
            return "[DEV MODE] No API key configured. Running in offline/local mode. Set Z.AI key in config.ini or start Ollama for local AI.", round(time.time() - start_time, 2)
        base_url = None
    else:
        base_url = "https://api.z.ai/api/paas/v4/"
    
    if model is None:
        model = config.get_ai_model()
        if model == "glm-5.1" and api_key:
            pass
        elif config.is_offline_mode():
            model = "gpt-4o-mini"

    try:
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        client = openai.OpenAI(**client_kwargs)
        
        user_context = format_user_context()
        messages = []
        if user_context:
            messages.append({"role": "system", "content": user_context})
        messages.append({"role": "user", "content": prompt})
        
        stream = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=config.get_temperature(),
            stream=True
        )

        print("Nova:", end=" ", flush=True)
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                full_response += chunk.choices[0].delta.content
        print()
        return full_response.strip(), round(time.time() - start_time, 2)

    except openai.AuthenticationError:
        return "[WARN] Authentication failed. Please check your API key in config.ini.", round(time.time() - start_time, 2)
    except openai.RateLimitError:
        return "[WARN] Rate limit exceeded. Please wait a moment and try again.", round(time.time() - start_time, 2)
    except Exception as e:
        return f"[ERROR] {str(e)}", round(time.time() - start_time, 2)
