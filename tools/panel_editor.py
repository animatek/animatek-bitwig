#!/usr/bin/env python3
"""Panel editor for our Bitwig devices: move the panel's elements with the mouse.

Serves tools/panel_editor.html on http://127.0.0.1:4310 (this machine only) and edits the
device's layout.json. "Save & build" writes layout.json and runs the device's build.py, which
copies the new .bwdevice into the Patchbay test folder; then restart Bitwig from Patchbay.

    tools/panel_editor.py                       # ATEK303 (devices-src/atek303)
    tools/panel_editor.py devices-src/other     # another device with layout.json + document.py

Run it with the blueprint's Python (the device's document.py imports the blueprint helpers):
    terceros/bitwig-devices-blueprint/.venv/bin/python tools/panel_editor.py
"""
from __future__ import annotations

import json
import subprocess
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
BLUEPRINT = REPO / "terceros/bitwig-devices-blueprint"
PORT = 4310


def load_parameters(workspace: Path) -> list[dict]:
    """The device's parameters (title, kind, choices), read from its document.py."""
    sys.path[:0] = [str(BLUEPRINT), str(BLUEPRINT / "scripts"), str(workspace)]
    import document  # noqa: E402  (the device's own document.py)
    out = []
    for spec in document.PARAMETERS:
        kind, title, ident, _port, default, tooltip = spec[:6]
        entry = {"id": ident, "title": title, "kind": kind, "tooltip": tooltip}
        if kind == "idx":
            entry["choices"] = [c.split("|")[0] for c in default]
        out.append(entry)
    return out


def make_handler(workspace: Path, parameters: list[dict]):
    layout_file = workspace / "layout.json"
    page = Path(__file__).with_name("panel_editor.html")

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def send(self, code: int, body: bytes, kind: str = "application/json"):
            self.send_response(code)
            self.send_header("Content-Type", kind)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self.send(200, page.read_bytes(), "text/html; charset=utf-8")
            elif self.path == "/api/layout":
                self.send(200, layout_file.read_bytes())
            elif self.path == "/api/params":
                self.send(200, json.dumps({"device": workspace.name, "params": parameters}).encode())
            else:
                self.send(404, b'{"error": "not found"}')

        def do_POST(self):
            if not self.path.startswith("/api/save"):
                return self.send(404, b'{"error": "not found"}')
            length = int(self.headers.get("Content-Length", 0))
            try:
                layout = json.loads(self.rfile.read(length))
                assert isinstance(layout.get("sections"), list) and "panel" in layout
            except Exception as exc:  # malformed body: refuse, keep the file as it is
                return self.send(400, json.dumps({"error": f"invalid layout: {exc}"}).encode())
            layout_file.write_text(json.dumps(layout, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            result = {"saved": str(layout_file)}
            if "build=1" in self.path:
                done = subprocess.run([sys.executable, str(workspace / "build.py")], cwd=workspace,
                                      capture_output=True, text=True, timeout=120)
                result["build_ok"] = done.returncode == 0
                result["build_output"] = (done.stdout + done.stderr)[-3000:]
            self.send(200, json.dumps(result).encode())

    return Handler


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    workspace = (REPO / (args[0] if args else "devices-src/atek303")).resolve()
    if not (workspace / "layout.json").is_file():
        print(f"No layout.json in {workspace}", file=sys.stderr)
        return 1
    parameters = load_parameters(workspace)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), make_handler(workspace, parameters))
    url = f"http://127.0.0.1:{PORT}/"
    print(f"Panel editor for {workspace.name}: {url}  (Ctrl+C to stop)")
    if "--no-browser" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
