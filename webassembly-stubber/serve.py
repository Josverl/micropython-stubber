"""
Custom HTTP server for the webassembly-stubber.

Extends Python's SimpleHTTPRequestHandler with two extra capabilities:
  1.  GET /firmware/webassembly/?format=json
        Returns a JSON array of local firmware names derived from zip files.
  2.  GET /firmware/webassembly/{name}/micropython.mjs
      GET /firmware/webassembly/{name}/micropython.wasm
        Serves the file from inside the corresponding zip on the fly.

All other requests are handled normally by SimpleHTTPRequestHandler.

Usage:
    python serve.py           # serves on http://127.0.0.1:8000/
    python serve.py 8080      # custom port
"""

import json
import os
import sys
import urllib.parse
import zipfile
from http.server import HTTPServer, SimpleHTTPRequestHandler

WEBASSEMBLY_DIR = "firmware/webassembly"


class ZipAwareHandler(SimpleHTTPRequestHandler):
    """Serve static files + files from inside local WASM zip bundles."""

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        super().end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path   = parsed.path
        qs     = urllib.parse.parse_qs(parsed.query)

        # ── JSON list of local firmware names ────────────────────────────────
        if path.rstrip("/") == f"/{WEBASSEMBLY_DIR}" and qs.get("format") == ["json"]:
            names = sorted(
                f[:-4] for f in os.listdir(WEBASSEMBLY_DIR)
                if f.endswith(".zip")
            )
            data = json.dumps(names).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # ── Serve micropython.mjs / .wasm from inside a zip ──────────────────
        prefix = f"/{WEBASSEMBLY_DIR}/"
        if path.startswith(prefix):
            rest  = path[len(prefix):]          # "{name}/micropython.mjs"
            parts = rest.split("/")
            if len(parts) == 2:
                name, filename = parts
                if filename in ("micropython.mjs", "micropython.wasm"):
                    zip_path = os.path.join(WEBASSEMBLY_DIR, name + ".zip")
                    if os.path.exists(zip_path):
                        try:
                            with zipfile.ZipFile(zip_path) as zf:
                                if filename in zf.namelist():
                                    data  = zf.read(filename)
                                    ctype = (
                                        "text/javascript"
                                        if filename.endswith(".mjs")
                                        else "application/wasm"
                                    )
                                    self.send_response(200)
                                    self.send_header("Content-Type", ctype)
                                    self.send_header("Content-Length", str(len(data)))
                                    self.end_headers()
                                    self.wfile.write(data)
                                    return
                        except zipfile.BadZipFile:
                            pass

        # ── Default: serve from filesystem ───────────────────────────────────
        super().do_GET()

    def log_message(self, fmt, *args):
        # Suppress /favicon.ico noise
        if args and "/favicon.ico" in str(args[0]):
            return
        super().log_message(fmt, *args)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = HTTPServer(("127.0.0.1", port), ZipAwareHandler)
    print(f"Serving on http://127.0.0.1:{port}/")
    print(f"Local WASM zips from: {os.path.abspath(WEBASSEMBLY_DIR)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")


if __name__ == "__main__":
    main()
