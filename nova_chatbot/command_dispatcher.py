from .platform_utils import open_app
from .web_search import search_web
from .file_handler import handle_file_upload
from .object_recognition import object_recognizer
from .system_control import shutdown, restart

class CommandDispatcher:
    def __init__(self, plugins):
        self.commands = {
            "scan": self.scan,
            "upload": self.upload,
            "open": self.open,
            "search": self.search,
            "shutdown": self.shutdown,
            "restart": self.restart,
        }
        self.plugins = plugins

    def dispatch(self, user_input):
        parts = user_input.lower().split()
        command = parts[0]
        args = " ".join(parts[1:])

        if command.startswith("!"):
            return self.run_plugin(command[1:])

        if command in self.commands:
            return self.commands[command](args)

        return None

    def scan(self, args):
        print("🔍 Scanning using camera...")
        results = object_recognizer.recognize_objects()
        return "\n".join(results)

    def upload(self, args):
        return handle_file_upload(args)

    def open(self, args):
        return open_app(args)

    def search(self, args):
        results = search_web(args)
        output = []
        for r in results:
            output.append(f"- {r['title']}\n  {r['href']}\n  {r['body']}")
        return "\n".join(output)

    def run_plugin(self, plugin_name):
        if plugin_name in self.plugins:
            try:
                return self.plugins[plugin_name].run()
            except Exception as e:
                return f"❌ Plugin error: {e}"
        else:
            return f"⚠️ Plugin '{plugin_name}' not found."

    def shutdown(self, args):
        print("⚠️ This will shut down your computer. Make sure you have saved all your work.")
        return shutdown()

    def restart(self, args):
        print("⚠️ This will restart your computer. Make sure you have saved all your work.")
        return restart()
