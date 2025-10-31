import os
import subprocess
import platform
import psutil
import time

def run(user_input=None):
    return "Plugin 'windows_control' listens passively. Use '!windows_control open word' for commands."

def on_message(message, online_mode=False):
    message_lower = message.lower()
    if not message_lower.startswith("open "):
        return None

    app_name = message_lower[5:].strip()
    if not app_name:
        return "Please specify an app to open."

    # Try to open app via Windows start menu / shell command
    try:
        if platform.system() == "Windows":
            # Check running processes to avoid duplicate apps
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] and app_name.lower() in proc.info['name'].lower():
                    return f"{app_name.capitalize()} is already running."

            # Use 'start' command
            cmd = f'start shell:AppsFolder\\Microsoft.Windows.{app_name.capitalize()}'
            # This is very generic and may not work for all apps, fallback to start <app_name>
            subprocess.Popen(['start', app_name], shell=True)
            time.sleep(1)
            return f"Opening {app_name}..."
        else:
            return "Windows control plugin supports Windows only."
    except Exception as e:
        return f"Failed to open {app_name}: {e}"
