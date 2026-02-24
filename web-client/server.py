from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HOST = "0.0.0.0"
PORT = 8000
TIMEOUT_SECONDS = 120


class ProxyHandler(SimpleHTTPRequestHandler):
    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self) -> None:  # noqa: N802
        if self.path == "/api/generate":
            self.send_response(HTTPStatus.NO_CONTENT)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()
            return
        super().do_OPTIONS()

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/generate":
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Rota não encontrada."})
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            request_body = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "JSON inválido."})
            return

        endpoint = str(request_body.get("endpoint", "")).strip().rstrip("/")
        api_key = str(request_body.get("runpod_api_key", "")).strip()
        payload = request_body.get("payload")

        if not endpoint:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Campo endpoint é obrigatório."})
            return
        if not endpoint.startswith(("http://", "https://")):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "endpoint deve iniciar com http:// ou https://."})
            return
        if not api_key:
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Campo runpod_api_key é obrigatório."})
            return
        if not isinstance(payload, dict):
            self._send_json(HTTPStatus.BAD_REQUEST, {"error": "Campo payload deve ser um objeto JSON."})
            return

        target_url = endpoint if endpoint.endswith("/generate") else f"{endpoint}/generate"
        upstream_data = json.dumps(payload).encode("utf-8")
        upstream_request = urllib.request.Request(
            target_url,
            data=upstream_data,
            method="POST",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

        try:
            with urllib.request.urlopen(upstream_request, timeout=TIMEOUT_SECONDS) as response:
                status = response.status
                content_type = response.headers.get("Content-Type", "application/json")
                body = response.read()
                self.send_response(status)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        except urllib.error.HTTPError as exc:
            body = exc.read() if exc.fp else b""
            content_type = exc.headers.get("Content-Type", "application/json") if exc.headers else "application/json"
            self.send_response(exc.code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.URLError as exc:
            self._send_json(
                HTTPStatus.BAD_GATEWAY,
                {"error": "Falha ao conectar ao endpoint Runpod.", "details": str(exc.reason)},
            )


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), ProxyHandler)
    print(f"Servidor iniciado em http://{HOST}:{PORT}")
    print("Rota de proxy: POST /api/generate")
    server.serve_forever()
