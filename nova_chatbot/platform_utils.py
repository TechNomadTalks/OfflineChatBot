import platform
import subprocess
import os
import shlex

def open_app(app_name):
    system = platform.system()
    if system == "Windows":
        return open_app_windows(app_name)
    elif system == "Darwin":
        return open_app_macos(app_name)
    elif system == "Linux":
        return open_app_linux(app_name)
    else:
        return f"Unsupported operating system: {system}"

def open_app_windows(app_name):
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

def open_app_macos(app_name):
    try:
        subprocess.run(["open", "-a", app_name], check=True)
        return f"Opening {app_name}..."
    except FileNotFoundError:
        return f"❌ Application '{app_name}' not found."
    except subprocess.CalledProcessError:
        return f"❌ Failed to open '{app_name}'."

def open_app_linux(app_name):
    try:
        subprocess.Popen([app_name])
        return f"Opening {app_name}..."
    except FileNotFoundError:
        return f"❌ Command to open '{app_name}' not found. Make sure it's in your PATH."
