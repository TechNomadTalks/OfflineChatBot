"""
Command dispatcher - handles special commands.
"""

from .platform_utils import open_app
from .web_search import search_web
from .file_handler import handle_file_upload
from .object_recognition import object_recognizer
from .system_control import shutdown, restart
from .config import config


class CommandDispatcher:
    """Handles special commands that don't go to the AI."""
    
    def __init__(self, plugins):
        self.commands = {
            "scan": self.scan,
            "upload": self.upload,
            "open": self.open_app,
            "search": self.search,
            "shutdown": self.shutdown_computer,
            "restart": self.restart_computer,
            "clear": self.clear_memory,
            "voice": self.toggle_voice,
            "mode": self.show_mode,
            "export": self.export_memory,
            "import": self.import_memory,
            "find": self.find_in_memory,
            "look": self.look_at_image,
            "plan": self.create_plan,
        }
        self.plugins = plugins

    def dispatch(self, user_input):
        """
        Try to dispatch a command.
        
        Args:
            user_input: The user's input
            
        Returns:
            Response string if command was handled, None otherwise
        """
        parts = user_input.lower().split()
        
        if not parts:
            return None
            
        command = parts[0]
        args = " ".join(parts[1:])

        if command.startswith("!"):
            plugin_name = command[1:]
            if plugin_name in self.plugins:
                if not self.check_permission(plugin_name, command):
                    return f"[DENIED] Plugin '{plugin_name}' not allowed to run this command"
            return self.run_plugin(command[1:], args)

        if command in self.commands:
            return self.commands[command](args)

        return None

    def scan(self, args):
        """Scan for objects using camera."""
        print("[SCAN] Using camera...")
        results = object_recognizer.recognize_objects()
        return "\n".join(results)

    def upload(self, args):
        """Handle file upload."""
        if not args:
            return "⚠️ Please provide a file path. Usage: upload <filepath>"
        return handle_file_upload(args)

    def open_app(self, args):
        """Open an application."""
        if not args:
            return "⚠️ Please provide an app name. Usage: open <appname>"
        return open_app(args)

    def search(self, args):
        """Search the web."""
        if not args:
            return "⚠️ Please provide a search query. Usage: search <query>"
        results = search_web(args)
        if not results:
            return "No search results found."
        
        output = []
        for r in results:
            title = r.get('title', 'No title')
            href = r.get('href', '')
            body = r.get('body', '')[:200]
            output.append(f"{title}\n  {href}\n  {body}")
        return "\n\n".join(output)

    def shutdown_computer(self, args):
        """Shutdown the computer."""
        return shutdown()

    def restart_computer(self, args):
        """Restart the computer."""
        return restart()

    def clear_memory(self, args):
        """Clear conversation memory."""
        from .memory import clear_memory
        clear_memory()
        return "[OK] Memory cleared."

    def toggle_voice(self, args):
        """Toggle voice input on/off."""
        if args in ['on', 'enable', 'true']:
            try:
                from . import audio_input
                audio_input.start_voice_input()
                return "[OK] Voice input enabled."
            except FileNotFoundError as e:
                return f"[ERROR] Voice input unavailable: {e}"
            except Exception as e:
                return f"[ERROR] Could not start voice input: {e}"
        elif args in ['off', 'disable', 'false']:
            try:
                from . import audio_input
                audio_input.stop_voice_input()
                return "[OK] Voice input disabled."
            except Exception as e:
                return f"[ERROR] Could not stop voice input: {e}"
        else:
            try:
                from . import audio_input
                status = "enabled" if audio_input.speech_recognizer and audio_input.speech_recognizer.running else "disabled"
                return f"Voice input is {status}."
            except:
                return "Voice input is disabled (model not found)."

    def show_mode(self, args):
        """Show current AI mode."""
        if config.is_offline_mode():
            return "[OFFLINE] Current mode: Offline (using Ollama)"
        else:
            return f"[ONLINE] Current mode: Online ({config.get_ai_model()})"

    def export_memory(self, args):
        """Export memory to a file."""
        if not args:
            return "[ERROR] Usage: export <filepath>"
        from .memory import export_memory
        success, msg = export_memory(args)
        return msg

    def import_memory(self, args):
        """Import memory from a file."""
        if not args:
            return "[ERROR] Usage: import <filepath>"
        from .memory import import_memory
        success, msg = import_memory(args)
        return msg

    def find_in_memory(self, args):
        """Search memory for a query."""
        if not args:
            return "[ERROR] Usage: find <query>"
        from .memory import search_memory
        results = search_memory(args)
        if not results:
            return "[INFO] No matches found."
        lines = [f"[{i}] You: {r.get('user','')} | Nova: {r.get('bot','')[:100]}" for i, r in enumerate(results)]
        return "\n".join(lines)

    def look_at_image(self, args):
        """Analyze an image file."""
        if not args or not os.path.exists(args):
            return "[ERROR] Usage: look <image_path>"
        from .object_recognition import object_recognizer
        results = object_recognizer.recognize_objects(args, online_mode=True)
        return "\n".join(results)

    def create_plan(self, args):
        """Create and execute a plan for a task."""
        if not args:
            return "[ERROR] Usage: plan <task_description>"
        from .planner import plan_task, execute_plan
        plan = plan_task(args)
        if not plan:
            return "[ERROR] Could not create plan"
        return execute_plan(plan)

    def run_plugin(self, plugin_name, args):
        """Run a plugin."""
        if plugin_name in self.plugins:
            try:
                plugin = self.plugins[plugin_name]
                if hasattr(plugin, 'run'):
                    return plugin.run(args)
                elif hasattr(plugin, 'on_message'):
                    return plugin.on_message(args)
                else:
                    return f"Plugin '{plugin_name}' has no run() or on_message() function."
            except Exception as e:
                return f"Plugin error: {e}"
        else:
            available = ", ".join(self.plugins.keys()) if self.plugins else "none"
            return f"Plugin '{plugin_name}' not found. Available: {available}"

    def check_permission(self, plugin_name, command):
        """Check if plugin is allowed to run a command."""
        permissions = config.get('permissions', plugin_name, '')
        if not permissions:
            return True
        allowed = [c.strip() for c in permissions.split(',') if c.strip()]
        return command in allowed
