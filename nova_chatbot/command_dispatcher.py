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

        # Check for plugin commands
        if command.startswith("!"):
            return self.run_plugin(command[1:], args)

        # Check built-in commands
        if command in self.commands:
            return self.commands[command](args)

        return None

    def scan(self, args):
        """Scan for objects using camera."""
        print("🔍 Scanning using camera...")
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
            body = r.get('body', '')[:200]  # Truncate body
            output.append(f"• {title}\n  {href}\n  {body}")
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
        return "✅ Memory cleared."

    def toggle_voice(self, args):
        """Toggle voice on/off."""
        if args in ['on', 'enable', 'true']:
            return "⚠️ Voice is always enabled in config. Edit config.ini to change."
        elif args in ['off', 'disable', 'false']:
            return "⚠️ Voice is always enabled in config. Edit config.ini to change."
        else:
            return f"Voice is {'enabled' if config.is_voice_enabled() else 'disabled'}"

    def show_mode(self, args):
        """Show current AI mode."""
        if config.is_offline_mode():
            return "📴 Current mode: Offline (using Ollama)"
        else:
            return f"🌐 Current mode: Online ({config.get_ai_model()})"

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
                    return f"⚠️ Plugin '{plugin_name}' has no run() or on_message() function."
            except Exception as e:
                return f"❌ Plugin error: {e}"
        else:
            available = ", ".join(self.plugins.keys()) if self.plugins else "none"
            return f"⚠️ Plugin '{plugin_name}' not found. Available: {available}"
