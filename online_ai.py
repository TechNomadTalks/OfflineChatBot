import time
import openai

client = openai.OpenAI()  # Uses env vars like OPENAI_API_KEY

def get_online_response(prompt: str) -> tuple[str, float]:
    start_time = time.time()
    full_response = ""

    try:
        stream = client.chat.completions.create(
            model="gpt-4o-mini",  # or your preferred model
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

    except Exception as e:
        # Catch all exceptions here to avoid import error on openai.error
        return f"❌ Error: {str(e)}", round(time.time() - start_time, 2)
