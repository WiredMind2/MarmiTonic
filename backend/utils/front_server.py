
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import threading


class FrontendHTTPRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        directory = os.path.join(os.path.dirname(__file__), '..', '..', 'frontend')
        super().__init__(*args, directory=directory, **kwargs)

def start_frontend_server():
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, FrontendHTTPRequestHandler)
    print(f"Starting frontend server on: http://localhost:8080")
    httpd.serve_forever()

# Start frontend server in a separate thread only if not already started
frontend_thread = None


def start_frontend_server_once():
    global frontend_thread
    if frontend_thread is None or not frontend_thread.is_alive():
        frontend_thread = threading.Thread(target=start_frontend_server, daemon=True)
        frontend_thread.start()
        print(f"Starting frontend server on: http://localhost:8080")
    else:
        print(f"Frontend server already running on: http://localhost:8080")