"""
Nova Chatbot - Main entry point.
"""

import os
import sys
import time
import importlib.util

from .config import config
from .voice import speak
from .ai_core import get_ai_response, switch_ai_mode, get_current_mode, trim_history
from .local_ai import local_ai
from .online_ai import get_online_response
from .memory import recall_memory, store_memory
from .object_recognition import object_recognizer
from .platform_utils import open_app
from .web_search import search_web
from .file_handler import handle_file_upload
from .command_dispatcher import CommandDispatcher
from .proactive_messaging import ProactiveMessenger
from .autonomous import run_autonomous
from .visualizer import start_visualizer, stop_visualizer
from .user_profile import get_username, ask_for_username, update_preference, learn_info, get_user_context, format_user_context
import nova_chatbot.audio_input as audio_input


_history = []
_history_index = 0

try:
    import readline
except ImportError:
    readline = None


def _add_to_history(text):
    global _history, _history_index
    if not text or (len(_history) > 0 and _history[-1] == text):
        return
    _history.append(text)
    _history_index = len(_history)
    if len(_history) > 1000:
        _history = _history[-1000:]


def _get_input_with_history(prompt):
    global _history_index
    if readline:
        readline.set_auto_history(True)
        readline.readline_history_file(os.path.expanduser("~/.nova_history"))
    try:
        text = input(prompt)
    except EOFError:
        return None
    _add_to_history(text.strip())
    return text.strip()


def load_plugins():
    """Load plugin modules from the plugins directory."""
    plugins = {}
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    
    if not os.path.isdir(plugins_dir):
        print("Plugins folder not found, skipping plugin load.")
        return plugins

    for file in os.listdir(plugins_dir):
        if file.endswith(".py") and not file.startswith("_"):
            path = os.path.join(plugins_dir, file)
            name = file[:-3]
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugins[name] = module
                print(f"[OK] Loaded plugin: {name}")
            except Exception as e:
                print(f"[WARN] Failed loading plugin '{name}': {e}")
    
    return plugins


def print_banner():
    """Print the welcome banner."""
    print(r"""
 ____   _______  _______
/    \ /  _ \  \/ /\__  \
|   |  (  <_> )   /  / __ \_  v2.0
|___|  /\____/ \_/  (____  /
     \/                  \/
    """)


def print_help():
    """Print available commands."""
    print("\n[COMMANDS] Available Commands:")
    print("  scan              - Scan objects with camera")
    print("  upload <path>     - Upload and process a file")
    print("  open <app>        - Open an application")
    print("  search <query>    - Search the web")
    print("  look <image>      - Analyze an image (GPT-4V style)")
    print("  plan <task>       - Create a plan for a task")
    print("  online mode       - Switch to Z.AI GLM-5.1")
    print("  offline mode      - Switch to local AI (Ollama)")
    print("  voice on/off      - Enable/disable voice input")
    print("  export <file>     - Export memory to JSON file")
    print("  import <file>     - Import memory from JSON file")
    print("  find <query>      - Search memory for entries")
    print("  !<plugin>         - Run a plugin")
    print("  help              - Show this help")
    print("  exit              - Exit the chatbot")
    print()


def main():
    """Main chatbot loop."""
    print_banner()
    
    # Check configuration
    if config.is_offline_mode():
        print("[MODE] Offline (using local Ollama)")
    else:
        api_key = config.get_zai_api_key()
        if api_key:
            print(f"[MODE] Online (Z.AI GLM-5.1)")
        else:
            print("No API key found. Using offline mode.")
    
    # Check voice
    if not config.is_voice_enabled():
        print("[VOICE] Output disabled")
    
    print(f"\nWelcome to Nova")
    print_help()

    username = get_username()
    if not username or username == "User":
        username = ask_for_username()
    if config.is_visualizer_enabled():
        start_visualizer(username)

    # Load plugins
    plugins = load_plugins()
    
    # Initialize components
    command_dispatcher = CommandDispatcher(plugins)
    proactive_messenger = None
    
    if config.is_proactive_enabled():
        proactive_messenger = ProactiveMessenger()
        proactive_messenger.start()

    if config.is_visualizer_enabled():
        start_visualizer(config.get_visualizer_username())

    # Get memory setting
    memory_enabled = config.is_memory_enabled()

    while True:
        try:
            user_input = _get_input_with_history("You: ")
            if user_input is None:
                print("\n[GOODBYE] Goodbye!")
                if proactive_messenger:
                    proactive_messenger.stop()
                stop_visualizer()
                break

            if not user_input:
                continue

            # Handle commands
            user_input_lower = user_input.lower()
            
            if user_input_lower == "exit":
                print("[GOODBYE] Goodbye!")
                if proactive_messenger:
                    proactive_messenger.stop()
                stop_visualizer()
                break

            if user_input_lower == "help":
                print_help()
                continue

            if user_input_lower.startswith("autonomous ") or user_input_lower == "autonomous":
                cmd = user_input_lower.replace("autonomous ", "").strip()
                if not cmd:
                    print("[AI] Autonomous mode: specify 'analyze', 'suggest', 'review', or 'check'")
                    continue
                result = run_autonomous(cmd)
                print(f"Jarvis: {result}")
                if config.is_voice_enabled():
                    speak(result)
                continue

            if user_input_lower == "online mode":
                switch_ai_mode('glm-5.1')
                print("[MODE] Switched to Online Mode (Z.AI GLM-5.1)")
                continue

            if user_input_lower == "offline mode":
                switch_ai_mode('phi-3')
                print("[MODE] Switched to Offline Mode")
                continue

            if user_input_lower == "voice on":
                try:
                    audio_input.start_voice_input()
                    print("[VOICE] Input enabled. Say something!")
                except FileNotFoundError as e:
                    print(f"[ERROR] Voice input unavailable: {e}")
                except Exception as e:
                    print(f"[ERROR] Could not start voice input: {e}")
                continue

            if user_input_lower == "voice off":
                try:
                    audio_input.stop_voice_input()
                    print("[VOICE] Input disabled.")
                except Exception as e:
                    print(f"[ERROR] Could not stop voice input: {e}")
                continue

            # Check for voice input result
            if config.is_memory_enabled():
                voice_text = audio_input.get_voice_text()
                if voice_text:
                    user_input = voice_text
                    print(f"[VOICE] You (voice): {user_input}")

            # Try command dispatcher first
            response = command_dispatcher.dispatch(user_input)
            if response:
                print(f"Nova: {response}")
                if config.is_voice_enabled():
                    speak(response)
                continue

            # Get chat history for context
            if memory_enabled:
                try:
                    chat_history = recall_memory()
                    model = config.get_ai_model() if not config.is_offline_mode() else 'phi-3'
                    chat_history = trim_history(chat_history, model)
                except Exception as e:
                    print(f"[ERROR] Memory error: {e}")
                    chat_history = []
            else:
                chat_history = []

            # Get AI response
            start_time = time.time()
            response, duration = get_ai_response(user_input, chat_history or [])
            
            print(f"Nova: {response}")
            if config.is_voice_enabled():
                speak(response)

            if memory_enabled:
                try:
                    store_memory(user_input, response)
                except Exception as e:
                    print(f"[WARN] Memory store error: {e}")

            if "what is your name" in user_input.lower() or "your name" in user_input.lower():
                learn_info("name_preference", "asked")
            if "i am" in user_input.lower() or "i'm" in user_input.lower():
                import re
                match = re.search(r"(?:i am|i'm)\s+(\w+)", user_input, re.IGNORECASE)
                if match:
                    learn_info("name", match.group(1))

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"[ERROR] Unexpected error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If a command is provided as a command-line argument, run it and exit
        command = " ".join(sys.argv[1:])
        
        print(f"Running command: {command}")
        
        # Load plugins and run command
        plugins = load_plugins()
        command_dispatcher = CommandDispatcher(plugins)
        
        response = command_dispatcher.dispatch(command)
        if response:
            print(f"Nova: {response}")
        else:
            # If the command is not a dispatcher command, try AI
            chat_history = []
            if config.is_memory_enabled():
                try:
                    chat_history = recall_memory()
                    model = config.get_ai_model() if not config.is_offline_mode() else 'phi-3'
                    chat_history = trim_history(chat_history, model)
                except Exception:
                    chat_history = []
            response, _ = get_ai_response(command, chat_history)
            print(f"Nova: {response}")
    else:
        # Run the interactive main loop
        main()
