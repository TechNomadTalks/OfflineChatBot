"""
Nova Chatbot - Main entry point.
"""

import os
import sys
import time
import importlib.util

from .config import config
from .voice import speak
from .ai_core import get_ai_response, switch_ai_mode, get_current_mode
from .local_ai import local_ai
from .online_ai import get_online_response
from .vector_memory import recall_memory, store_memory
from .object_recognition import object_recognizer
from .platform_utils import open_app
from .web_search import search_web
from .file_handler import handle_file_upload
from .command_dispatcher import CommandDispatcher
from .proactive_messaging import ProactiveMessenger


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
                print(f"✅ Loaded plugin: {name}")
            except Exception as e:
                print(f"⚠️ Failed loading plugin '{name}': {e}")
    
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
    print("\n📚 Available Commands:")
    print("  scan              - Scan objects with camera")
    print("  upload <path>    - Upload and process a file")
    print("  open <app>       - Open an application")
    print("  search <query>   - Search the web")
    print("  online mode      - Switch to OpenAI (requires API key)")
    print("  offline mode     - Switch to local AI (Ollama)")
    print("  !<plugin>        - Run a plugin")
    print("  help             - Show this help")
    print("  exit             - Exit the chatbot")
    print()


def main():
    """Main chatbot loop."""
    print_banner()
    
    # Check configuration
    if config.is_offline_mode():
        print("📴 Mode: Offline (using local Ollama)")
    else:
        api_key = config.get_openai_api_key()
        if api_key:
            print(f"🌐 Mode: Online ({config.get_ai_model()})")
        else:
            print("⚠️ No API key found. Using offline mode.")
    
    # Check voice
    if not config.is_voice_enabled():
        print("🔇 Voice output disabled")
    
    print(f"\nWelcome to Nova ✨")
    print_help()

    # Load plugins
    plugins = load_plugins()
    
    # Initialize components
    command_dispatcher = CommandDispatcher(plugins)
    proactive_messenger = None
    
    if config.is_proactive_enabled():
        proactive_messenger = ProactiveMessenger()
        proactive_messenger.start()

    # Get memory setting
    memory_enabled = config.is_memory_enabled()

    while True:
        try:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                print("\nGoodbye!")
                if proactive_messenger:
                    proactive_messenger.stop()
                break

            if not user_input:
                continue

            # Handle commands
            user_input_lower = user_input.lower()
            
            if user_input_lower == "exit":
                print("👋 Goodbye!")
                if proactive_messenger:
                    proactive_messenger.stop()
                break

            if user_input_lower == "help":
                print_help()
                continue

            if user_input_lower == "online mode":
                switch_ai_mode('gpt-4o-mini')
                print("✅ Switched to Online Mode")
                continue

            if user_input_lower == "offline mode":
                switch_ai_mode('phi-3')
                print("✅ Switched to Offline Mode")
                continue

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
                    chat_history = recall_memory(user_input)
                except Exception as e:
                    print(f"⚠️ Memory error: {e}")
                    chat_history = []
            else:
                chat_history = []

            # Get AI response
            start_time = time.time()
            response, duration = get_ai_response(user_input, chat_history or [])
            
            print(f"Nova: {response}")
            if config.is_voice_enabled():
                speak(response)

            # Store in memory
            if memory_enabled:
                try:
                    store_memory(user_input, response)
                except Exception as e:
                    print(f"⚠️ Memory store error: {e}")

        except KeyboardInterrupt:
            print("\n\nInterrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
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
            response, _ = get_ai_response(command, chat_history)
            print(f"Nova: {response}")
    else:
        # Run the interactive main loop
        main()
