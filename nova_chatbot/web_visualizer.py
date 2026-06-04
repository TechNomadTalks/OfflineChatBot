"""
Web-based visualizer server for Nova Chatbot.
Serves the HTML5 Canvas particle system.
"""

import http.server
import socketserver
import os
import threading

PORT = 8080
VISUALIZER_DIR = os.path.join(os.path.dirname(__file__), 'visualizer')


def start_server():
    os.makedirs(VISUALIZER_DIR, exist_ok=True)
    
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=VISUALIZER_DIR, **kwargs)
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"[Visualizer] Web server running at http://localhost:{PORT}")
        httpd.serve_forever()


def start_visualizer_server():
    thread = threading.Thread(target=start_server, daemon=True)
    thread.start()
    return thread