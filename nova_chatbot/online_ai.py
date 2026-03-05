"""
Online AI integration using OpenAI API.
"""

import time
import openai
from .config import config


def get_online_response(prompt: str, model: str = None) -> tuple[str, float]:
    """
    Get a response from OpenAI API.
    
    Args:
        prompt: The user's prompt
        model: The model to use (default: from config)
    
    Returns:
        Tuple of (response_text, elapsed_time)
    """
    start_time = time.time()
    full_response = ""
    
    # Check for API key
    api_key = config.get_openai_api_key()
    if not api_key:
        return "⚠️ OpenAI API key not configured. Please set your API key in config.ini or set OPENAI_API_KEY environment variable.", round(time.time() - start_time, 2)
    
    # Get model from config if not specified
    if model is None:
        model = config.get_ai_model()
        # If offline mode is on, default to a small model
        if config.is_offline_mode():
            model = "gpt-4o-mini"

    try:
        # Initialize OpenAI client with API key
        client = openai.OpenAI(api_key=api_key)
        
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stream=True
        )

        print("Nova:", end=" ", flush=True)
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                full_response += chunk.choices[0].delta.content
        print()  # newline after full output
        return full_response.strip(), round(time.time() - start_time, 2)

    except openai.AuthenticationError:
        return "⚠️ Authentication failed. Please check your OpenAI API key in config.ini.", round(time.time() - start_time, 2)
    except openai.RateLimitError:
        return "⚠️ Rate limit exceeded. Please wait a moment and try again.", round(time.time() - start_time, 2)
    except Exception as e:
        return f"❌ Error: {str(e)}", round(time.time() - start_time, 2)
