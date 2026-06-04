"""
Skill graph / planning module for task decomposition.
"""

from .config import config
from .online_ai import get_online_response
from .local_ai import local_ai


def plan_task(task_description):
    """Break down a task into sub-tasks."""
    prompt = f"""Break down this task into 3-5 simple steps that can be executed by a CLI chatbot.
Task: {task_description}

Return a JSON array of steps, where each step is a simple action like:
- "run python script.py"
- "open browser"
- "check file /path/to/file"
- "search web for ..."
- "edit file /path/to/file"

Format:
["step 1", "step 2", "step 3"]

Do not add any other text or explanation."""
    
    if config.is_offline_mode():
        return local_ai.generate_local_response(prompt, [])[0]
    
    api_key = config.get_zai_api_key() or config.get_openai_api_key_fallback()
    if not api_key:
        return None
    
    try:
        import json
        import openai
        
        base_url = "https://api.z.ai/api/paas/v4/" if config.get_zai_api_key() else None
        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url
        
        client = openai.OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=config.get_ai_model(),
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception:
        return None


def execute_plan(plan):
    """Execute a plan step by step."""
    if not plan:
        return "[ERROR] No plan to execute"
    
    results = []
    for i, step in enumerate(plan, 1):
        results.append(f"[STEP {i}/{len(plan)}] {step}")
    return "\n".join(results)