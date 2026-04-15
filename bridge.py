"""
ADAM Chat Bridge - Python version
No install needed. Python 3 is already on Windows 10/11.
Run with: python bridge.py
"""

import json, os, urllib.request, urllib.error, threading, webbrowser
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 3000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Load config.json for API keys ─────────────────────────────────────────────
config = {}
config_path = os.path.join(BASE_DIR, "config.json")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        config = json.load(f)


class BridgeHandler(SimpleHTTPRequestHandler):

    # Silence the default request log spam
    def log_message(self, format, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/health":
            self._json(200, {"status": "ok", "message": "ADAM Bridge is running ✅"})
        else:
            # Serve static files (index.html etc.)
            self.directory = BASE_DIR
            super().do_GET()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)

        if self.path == "/v1/messages":
            self._proxy_anthropic(body)
        elif self.path == "/v1/chat/completions":
            self._proxy_openai(body)
        else:
            self._json(404, {"error": "Unknown endpoint"})

    # ── Anthropic proxy ───────────────────────────────────────────────────────
    def _proxy_anthropic(self, body):
        api_key = self.headers.get("x-api-key") or config.get("anthropic_key", "")
        if not api_key:
            self._json(400, {"error": {"message": "No Anthropic API key. Enter it in the 🔑 panel."}})
            return
        try:
            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=body,
                headers={
                    "x-api-key":          api_key,
                    "anthropic-version":  self.headers.get("anthropic-version", "2023-06-01"),
                    "Content-Type":       "application/json",
                },
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._json(500, {"error": {"message": str(e)}})

    # ── OpenAI proxy ──────────────────────────────────────────────────────────
    def _proxy_openai(self, body):
        auth = self.headers.get("Authorization") or ("Bearer " + config.get("openai_key", ""))
        try:
            req = urllib.request.Request(
                "https://api.openai.com/v1/chat/completions",
                data=body,
                headers={"Authorization": auth, "Content-Type": "application/json"},
                method="POST"
            )
            with urllib.request.urlopen(req) as resp:
                data = resp.read()
                self.send_response(200)
                self._cors()
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self._cors()
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self._json(500, {"error": {"message": str(e)}})

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin",  "*")
        self.send_header("Access-Control-Allow-Methods", "GET,POST,OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "x-api-key,anthropic-version,content-type,authorization")

    def _json(self, code, obj):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(data)


# ── Start ─────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    server = HTTPServer(("localhost", PORT), BridgeHandler)

    print()
    print("╔══════════════════════════════════════╗")
    print("║     ADAM BRIDGE  ✅  RUNNING (Py)    ║")
    print("╚══════════════════════════════════════╝")
    print()
    print("  👉  Your browser will open automatically.")
    print(f"      Or go to: http://localhost:{PORT}")
    print()
    print("  ⛔  Press Ctrl+C to stop")
    print()

    # Open browser after short delay
    threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Bridge stopped.")
