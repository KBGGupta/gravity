import os
import json
import mimetypes
import http.server
import socketserver
import threading
from urllib.parse import urlparse, parse_qs

from config import load_config, save_config, reset_to_default_config
from agent.brain import AgentBrain
from tools.file_tools import list_directory
from tools.git_tools import git_status, git_diff, git_log, git_commit
from tools.db_tools import sqlite_list_tables, sqlite_query
from accessibility import speaker

class AgentServerState:
    def __init__(self):
        self.config = load_config()
        self.messages = []
        self.status_text = "Ready"
        self.is_running = False
        self.lock = threading.Lock()
        self.on_workspace_pick_callback = None

        self.agent = AgentBrain(
            self.config,
            on_message=self.record_message,
            on_status=self.set_status
        )

    def record_message(self, role: str, content: str, extra=None):
        with self.lock:
            self.messages.append({
                "role": role,
                "content": content,
                "extra": extra
            })

    def set_status(self, status: str):
        with self.lock:
            self.status_text = status

    def update_config(self, new_config: dict):
        with self.lock:
            self.config.update(new_config)
            save_config(self.config)
            self.agent.update_config(self.config)

state = AgentServerState()

class AgentHttpHandler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        # Silence console log noise
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/api/config":
            self.send_json(state.config)
        elif path == "/api/messages":
            query = parse_qs(parsed.query)
            since = int(query.get("since", [0])[0])
            with state.lock:
                new_msgs = state.messages[since:]
                data = {
                    "messages": new_msgs,
                    "is_running": state.agent.is_running,
                    "status_text": state.status_text
                }
            self.send_json(data)
        elif path == "/api/tools/files":
            ws = state.config.get("workspace_dir", ".")
            out = list_directory(ws, ".")
            self.send_json({"output": out})
        else:
            # Serve static files from 'ui' directory
            rel_path = path.lstrip("/")
            if not rel_path or rel_path == "":
                rel_path = "index.html"
            
            ui_dir = os.path.join(os.path.dirname(__file__), "ui")
            file_path = os.path.normpath(os.path.join(ui_dir, rel_path))

            if os.path.exists(file_path) and os.path.isfile(file_path):
                ctype, _ = mimetypes.guess_type(file_path)
                ctype = ctype or "application/octet-stream"
                try:
                    with open(file_path, "rb") as f:
                        content = f.read()
                    self.send_response(200)
                    self.send_header("Content-Type", ctype)
                    self.send_header("Content-Length", str(len(content)))
                    self.end_headers()
                    self.wfile.write(content)
                except Exception as e:
                    self.send_response(500)
                    self.end_headers()
            else:
                self.send_response(404)
                self.end_headers()

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length > 0 else "{}"
        try:
            payload = json.loads(body)
        except Exception:
            payload = {}

        if path == "/api/prompt":
            prompt = payload.get("prompt", "").strip()
            if prompt:
                def _done():
                    state.set_status("Ready")
                state.agent.run_async(prompt, on_complete=_done)
                self.send_json({"status": "started"})
            else:
                self.send_json({"error": "Empty prompt"}, status=400)

        elif path == "/api/stop":
            state.agent.stop()
            self.send_json({"status": "stopped"})

        elif path == "/api/clear":
            with state.lock:
                state.messages.clear()
            state.agent.clear_history()
            self.send_json({"status": "cleared"})

        elif path == "/api/config":
            state.update_config(payload)
            self.send_json({"status": "updated", "config": state.config})

        elif path == "/api/config/reset":
            ws = state.config.get("workspace_dir", ".")
            default_cfg = reset_to_default_config(ws)
            state.update_config(default_cfg)
            if default_cfg.get("voice_feedback", True):
                speaker.speak("Settings reset to Ollama default.")
            self.send_json({"status": "reset", "config": default_cfg})

        elif path == "/api/workspace/pick":
            new_path = None
            if state.on_workspace_pick_callback:
                new_path = state.on_workspace_pick_callback()
            self.send_json({"path": new_path})

        elif path == "/api/tools/git":
            action = payload.get("action", "status")
            ws = state.config.get("workspace_dir", ".")
            if action == "status":
                out = git_status(ws)
            elif action == "diff":
                out = git_diff(ws)
            elif action == "log":
                out = git_log(ws)
            elif action == "commit":
                out = git_commit(ws, payload.get("message", "Update from agent"))
            else:
                out = "Unknown git action"
            self.send_json({"output": out})

        elif path == "/api/tools/db":
            action = payload.get("action", "tables")
            ws = state.config.get("workspace_dir", ".")
            db_path = payload.get("db_path", "test.db")
            if action == "tables":
                out = sqlite_list_tables(ws, db_path)
            elif action == "query":
                out = sqlite_query(ws, db_path, payload.get("query", ""))
            else:
                out = "Unknown database action"
            self.send_json({"output": out})

        else:
            self.send_response(404)
            self.end_headers()

def start_server():
    server = socketserver.TCPServer(("127.0.0.1", 0), AgentHttpHandler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, port

if __name__ == "__main__":
    srv, p = start_server()
    print(f"Server started at http://127.0.0.1:{p}/")
    import time
    while True:
        time.sleep(1)
