"""PlantGuide Web Demo: tag picker + care card UI.

A lightweight HTTP server built on Python stdlib (no pip install needed
for the web server itself).  Serves a static index.html and exposes
JSON API endpoints that the frontend calls.

Usage:
    cd web && python3 server.py
    # Open http://127.0.0.1:8765
"""

from __future__ import annotations

import json
import mimetypes
import os
import sys
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# PlantGuide imports — add the project src to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC))
os.environ["PLANTGUIDE_DATA_DIR"] = str(PROJECT_ROOT / "data")

from plantguide.data.loader import list_species_files, load_species, load_species_catalog
from plantguide.care.cards import care_card_for_species, watering_hint
from plantguide.identify.pipeline import identify_from_tags
from plantguide.models.toy import tags_from_text

HOST = "127.0.0.1"
PORT = int(os.getenv("PLANTGUIDE_WEB_PORT", "8765"))
STATIC_DIR = Path(__file__).resolve().parent


def _collect_all_tags(catalog: list[dict]) -> list[str]:
    seen: set[str] = set()
    for sp in catalog:
        for tag in sp.get("tags") or []:
            seen.add(tag.strip())
    return sorted(seen)


class PlantGuideHandler(BaseHTTPRequestHandler):

    # ── helpers ──────────────────────────────────────────────────────

    def _send_json(self, data: object, status: int = 200) -> None:
        body = json.dumps(data, ensure_ascii=False, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_error(self, message: str, status: int = 400) -> None:
        self._send_json({"error": message}, status=status)

    def _send_static(self, path: str) -> None:
        filepath = STATIC_DIR / path
        if not filepath.exists() or not filepath.is_relative_to(STATIC_DIR):
            self._send_error("Not Found", 404)
            return
        mime, _ = mimetypes.guess_type(str(filepath))
        self.send_response(200)
        self.send_header("Content-Type", mime or "application/octet-stream")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        with open(filepath, "rb") as f:
            self.wfile.write(f.read())

    # ── routes ───────────────────────────────────────────────────────

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        params = parse_qs(parsed.query)

        try:
            if path == "" or path == "/" or path == "/index.html":
                self._send_static("index.html")

            elif path == "/api/tags":
                """Return all available trait tags."""
                catalog = load_species_catalog()
                tags = _collect_all_tags(catalog)
                self._send_json({"tags": tags, "count": len(tags)})

            elif path == "/api/species":
                """Return the full species catalog (id + common name + tags)."""
                catalog = load_species_catalog()
                summary = [
                    {"id": s["id"], "common_name": s["common_name"],
                     "scientific_name": s.get("scientific_name", ""),
                     "tags": s.get("tags", [])}
                    for s in catalog
                ]
                self._send_json({"species": summary, "count": len(summary)})

            elif path.startswith("/api/species/") and path.endswith("/care"):
                """GET /api/species/{id}/care → care card."""
                species_id = path.split("/")[3]
                try:
                    card = care_card_for_species(species_id)
                    self._send_json({"care": card})
                except KeyError:
                    self._send_error(f"Unknown species: {species_id}", 404)

            elif path.startswith("/api/species/") and path.endswith("/water"):
                """GET /api/species/{id}/water?season=summer → watering hint."""
                species_id = path.split("/")[3]
                season = params.get("season", ["summer"])[0]
                try:
                    hint = watering_hint(species_id, season)
                    self._send_json({"hint": hint})
                except KeyError:
                    self._send_error(f"Unknown species: {species_id}", 404)

            else:
                self._send_error("Not Found", 404)

        except Exception:
            traceback.print_exc()
            self._send_error("Internal Server Error", 500)

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        try:
            if path == "/api/identify":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len) if content_len else b"{}"
                payload = json.loads(body) if body else {}
                tags = payload.get("tags", [])
                top_k = int(payload.get("top_k", 5))

                if isinstance(tags, str):
                    tag_list = tags_from_text(tags)
                else:
                    tag_list = [str(t).strip() for t in tags if str(t).strip()]

                if not tag_list:
                    self._send_error("At least one tag is required", 400)
                    return

                result = identify_from_tags(tag_list, top_k=top_k, with_care=True)
                self._send_json(result)

            else:
                self._send_error("Not Found", 404)

        except Exception:
            traceback.print_exc()
            self._send_error("Internal Server Error", 500)

    def log_message(self, format, *args):
        if args:
            sys.stderr.write(f"[PlantGuide Web] {args[0]} {args[1]} {args[2]}\n")


def main():
    server = HTTPServer((HOST, PORT), PlantGuideHandler)
    print(f"🌿 PlantGuide Web Demo: http://{HOST}:{PORT}")
    print(f"   Tag picker + Care cards — press Ctrl+C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()