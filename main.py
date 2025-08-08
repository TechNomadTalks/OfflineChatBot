import os
import sys
import time
import importlib.util
import subprocess
import shlex
from dotenv import load_dotenv

sys.path.append(os.path.dirname(__file__))

from ai_modules.voice import speak
from ai_modules.local_ai import local_ai
from ai_modules.online_ai import get_online_response
from utils.memory import recall_memory, store_memory
from vision.object_recognition import object_recognizer

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

online_mode = False
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

def open_app_by_name(app_name: str) -> str:
    try:
        # Try Windows 'where' command to find exe
        result = subprocess.run(
            ['where', app_name],
            capture_output=True,
            text=True,
            shell=True
        )
        paths = result.stdout.strip().splitlines()
        exe_paths = [p for p in paths if os.path.isfile(p) and p.lower().endswith('.exe')]

        if not exe_paths:
            # Search Program Files folders recursively (slow)
            program_files = [os.environ.get('ProgramFiles', ''),
                            os.environ.get('ProgramFiles(x86)', '')]
            found = None
            for base_path in program_files:
                if not base_path:
                    continue
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if file.lower() == f"{app_name.lower()}.exe":
                            found = os.path.join(root, file)
                            break
                    if found:
                        break
                if found:
                    break
            if found:
                exe_paths.append(found)

        if not exe_paths:
            return f"❌ Could not find executable for '{app_name}'."

        exe_path = exe_paths[0]
        subprocess.Popen(shlex.quote(exe_path), shell=True)
        return f"Opening {app_name}..."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

def main():
    global online_mode

    print(r"""
 ____   _______  _______   
/    \ /  _ \  \/ /\__  \  
|   |  (  <_> )   /  / __ \_
|___|  /\____/ \_/  (____  /
     \/                  \/
    """)
    print("Welcome to Nova ✨")
    print("Commands: 'online mode', 'offline mode', 'upload <filepath>', '!pluginname', 'scan', 'exit'")

    load_plugins()

    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue

            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            if user_input.lower() == "online mode":
                online_mode = True
                print("✅ Switched to Online Mode")
                continue

            if user_input.lower() == "offline mode":
                online_mode = False
                print("✅ Switched to Offline Mode")
                continue

            if user_input.lower() == "scan":
                print("🔍 Scanning using camera...")
                results = object_recognizer.recognize_objects(online_mode=online_mode)
                for res in results:
                    print(res)
                continue

            if user_input.lower().startswith("upload "):
                filepath = user_input[7:].strip()
                # Your handle_file_upload implementation (not shown here)
                # result = handle_file_upload(filepath)
                # print(f"[File Analysis]\n{result}")
                continue

            if user_input.startswith("!"):
                plugin_name = user_input[1:]
                if plugin_name in plugins:
                    try:
                        output = plugins[plugin_name].run()
                        print(f"[Plugin Output]\n{output}")
                        speak(output)
                    except Exception as e:
                        print(f"❌ Plugin error: {e}")
                else:
                    print(f"⚠️ Plugin '{plugin_name}' not found.")
                continue

            if user_input.lower().startswith("open "):
                app_name = user_input[5:].strip()
                response = open_app_by_name(app_name)
                print(f"Nova: {response}")
                speak(response)
                continue

            if memory_enabled:
                chat_history = recall_memory()
            else:
                chat_history = []

            start_time = time.time()

            if online_mode:
                if not OPENAI_API_KEY:
                    print("❌ OpenAI API key missing! Cannot use online mode.")
                    continue
                response, _ = get_online_response(user_input)
            else:
                response, _ = local_ai.generate_response(user_input, chat_history or [])

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
    main()
