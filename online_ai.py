import time
import openai

client = openai.OpenAI()  # Uses env vars for credentials

def get_online_response(prompt: str) -> tuple[str, float]:
    start_time = time.time()
    full_response = ""

    try:
        stream = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            stream=True
        )

        print("Nova:", end=" ", flush=True)
        for chunk in stream:
            # The new streaming response in openai>=1.0.0
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
                full_response += chunk.choices[0].delta.content
        print()  # Newline after complete response
        return full_response.strip(), round(time.time() - start_time, 2)

    except Exception as e:
        return f"❌ Error: {str(e)}", round(time.time() - start_time, 2)

def is_online_mode(query: str) -> bool:
    online_triggers = {
        'search', 'find', 'current', 'latest',
        'recent', 'online', 'web', 'look up',
        'who is', 'what is', 'where is'
    }
    return any(trigger in query.lower() for trigger in online_triggers)