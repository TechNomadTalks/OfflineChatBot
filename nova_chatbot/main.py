import os
import sys
import time
import importlib.util
import subprocess
import shlex

from .config import config
from .voice import speak
from .ai_core import get_ai_response, switch_ai_mode
from .local_ai import local_ai
from .online_ai import get_online_response
from .vector_memory import recall_memory, store_memory
from .object_recognition import object_recognizer
from .platform_utils import open_app
from .web_search import search_web
from .file_handler import handle_file_upload
from .command_dispatcher import CommandDispatcher
from .proactive_messaging import ProactiveMessenger

OPENAI_API_KEY = config.get_openai_api_key()
memory_enabled = True
plugins = {}

def load_plugins():
    plugins_dir = os.path.join(os.path.dirname(__file__), "plugins")
    if not os.path.isdir(plugins_dir):
        print("Plugins folder not found, skipping plugin load.")
        return

    for file in os.listdir(plugins_dir):
        if file.endswith(".py"):
            path = os.path.join(plugins_dir, file)
            name = file[:-3]
            try:
                spec = importlib.util.spec_from_file_location(name, path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                plugins[name] = module
            except Exception as e:
                print(f"Failed loading plugin '{name}': {e}")

def main():

    print(r"""
 ____   _______  _______
/    \ /  _ \  \/ /\__  \
|   |  (  <_> )   /  / __ \_
|___|  /\____/ \_/  (____  /
     \/                  \/
    """)
    print("Welcome to Nova ✨")
    print("Commands: 'upload <filepath>', '!pluginname', 'scan', 'exit', 'open <appname>', 'search <query>'")

    load_plugins()
    command_dispatcher = CommandDispatcher(plugins)
    proactive_messenger = ProactiveMessenger()
    proactive_messenger.start()

    while True:
        try:
            try:
                user_input = input("You: ").strip()
            except EOFError:
                print("\nGoodbye!")
                proactive_messenger.stop()
                break

            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Goodbye!")
                proactive_messenger.stop()
                break

            if user_input.lower() == "online mode":
                switch_ai_mode('gpt-4o-mini')
                print("✅ Switched to Online Mode")
                continue

            if user_input.lower() == "offline mode":
                switch_ai_mode('phi-3')
                print("✅ Switched to Offline Mode")
                continue

            response = command_dispatcher.dispatch(user_input)
            if response:
                print(f"Nova: {response}")
                speak(response)
                continue

            if memory_enabled:
                chat_history = recall_memory(user_input)
            else:
                chat_history = []

            start_time = time.time()

            response, _ = get_ai_response(user_input, chat_history or [])

            duration = time.time() - start_time
            print(f"Nova: {response}\n(Response time: {duration:.2f}s)")
            speak(response)

            if memory_enabled:
                store_memory(user_input, response)

        except KeyboardInterrupt:
            print("\nInterrupted by user. Exiting.")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # If a command is provided as a command-line argument, run it and exit
        command = " ".join(sys.argv[1:])

        # This is a simplified version of the main loop for single command execution
        load_plugins()
        command_dispatcher = CommandDispatcher(plugins)
        response = command_dispatcher.dispatch(command)
        if response:
            print(f"Nova: {response}")
        else:
            # If the command is not a dispatcher command, it might be a request for the AI
            chat_history = []
            response, _ = get_ai_response(command, chat_history)
            print(f"Nova: {response}")

    else:
        # Otherwise, run the interactive main loop
        main()
