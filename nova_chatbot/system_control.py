import os
import platform

def shutdown():
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /s /t 1")
    elif system == "Linux" or system == "Darwin":
        os.system("sudo shutdown -h now")
    else:
        return f"Unsupported operating system: {system}"
    return "Shutting down..."

def restart():
    system = platform.system()
    if system == "Windows":
        os.system("shutdown /r /t 1")
    elif system == "Linux" or system == "Darwin":
        os.system("sudo shutdown -r now")
    else:
        return f"Unsupported operating system: {system}"
    return "Restarting..."
