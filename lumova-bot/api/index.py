
import json
import os

from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        secret = os.environ.get("TELEGRAM_WEBHOOK_SECRET", "")
        received_secret = self.headers.get(
            "X-Telegram-Bot-Api-Secret-Token", ""
        )

        if not secret or received_secret != secret:
            self.send_response(403)
            self.end_headers()
            self.wfile.write(b"Forbidden")
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 1024 * 1024:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Invalid request")
                return

            update = json.loads(self.rfile.read(length))
            if not isinstance(update, dict):
                raise ValueError("Invalid update")

        except (ValueError, json.JSONDecodeError):
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"Invalid JSON")
            return

        # Обработка обновления ботом будет добавлена следующим этапом.
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"ok":true,"received":true}')

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status":"webhook endpoint ready"}')

