import json
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any

from memory import MemoryStore


def create_handler(memory: MemoryStore) -> type[BaseHTTPRequestHandler]:
    class AutonomyHandler(BaseHTTPRequestHandler):
        def _send_json(self, payload: Any, status: int = 200) -> None:
            body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, html: str, status: int = 200) -> None:
            body = html.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:
            if self.path == "/api/state":
                self._send_json({
                    "decisions": memory.recent_decisions(15),
                    "knowledge": memory.get_knowledge(),
                    "hypotheses": memory.recent_hypotheses(10),
                    "observations": memory.recent_observations(10),
                })
                return

            html = """<!doctype html>
<html lang="tr">
<head>
  <meta charset="utf-8" />
  <title>Otonomi Sistemi Paneli</title>
  <style>
    body { font-family: sans-serif; margin: 24px; background: #111; color: #eee; }
    pre { background: #1c1c1c; padding: 16px; border-radius: 8px; overflow: auto; }
  </style>
</head>
<body>
  <h1>Otonomi Sistemi — Canlı Durum</h1>
  <p><a href="/api/state" style="color:#7cf;">/api/state JSON çıktısını görüntüle</a></p>
  <pre id="out">Yükleniyor...</pre>
  <script>
    async function refresh() {
      const r = await fetch('/api/state');
      const j = await r.json();
      document.getElementById('out').textContent = JSON.stringify(j, null, 2);
    }
    refresh();
    setInterval(refresh, 5000);
  </script>
</body>
</html>"""
            self._send_html(html)

        def log_message(self, format: str, *args: Any) -> None:
            return

    return AutonomyHandler


def start_web_server(host: str, port: int, memory: MemoryStore) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer((host, port), create_handler(memory))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server
