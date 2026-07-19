"""Standalone static web server for PlantGuide Web Demo (bounty #15).

Usage:
    python -m plantguide.web.serve
Opens http://localhost:8000 with the tag picker + care card UI.
The UI POSTs to the FastAPI /identify endpoint.
"""

from __future__ import annotations

import http.server
import json
import os
import socketserver
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).parent
INDEX = HERE / "index.html"
PORT = 8000


class PlantGuideHandler(http.server.SimpleHTTPRequestHandler):
    """Serves static files from the web directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HERE), **kwargs)

    def log_message(self, format, *args):
        """Quieter logging."""
        print(f"[web] {args[0]} {args[1]} {args[2]}")


def serve(port: int = PORT) -> None:
    """Start the static web server."""
    os.chdir(str(HERE))
    with socketserver.TCPServer(("", port), PlantGuideHandler) as httpd:
        print(f"\n  🪴 PlantGuide Web Demo running at:")
        print(f"     http://localhost:{port}")
        print(f"     Press Ctrl+C to stop.\n")
        httpd.serve_forever()


if __name__ == "__main__":
    serve()
