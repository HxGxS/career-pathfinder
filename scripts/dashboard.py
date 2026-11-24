#!/usr/bin/env python3
"""Open the Career Pathfinder dashboard on this computer, with your own fields editable.

The offline file (career_dashboard_*.html) shows everything but can't save. This small
local app serves the same page with a "Your notes" form in each role's details panel,
so you can change Status, Next Step, Next-Step Date and Notes directly. See
career-tracker-dashboard (the skill).

Each save:
  * changes only those four fields of that one role (nothing else can be edited);
  * writes a NEW version of the tracker data file (career_tracker_<today>[_vN].json),
    never overwriting the old one; and
  * rebuilds the matching offline dashboard file, so both stay in step.

Safety:
  * It listens on 127.0.0.1 only, so nothing outside this computer can reach it, and it
    refuses requests addressed to any other host name.
  * Saves need a secret code generated each time the app starts and built into the
    page; another website open in your browser can't know it, so it can't send changes.
  * Besides the page, it serves only your files in workspace/cvs/, workspace/letters/
    and workspace/job_descriptions/ (so the page's links open), never anything else.

Usage (from the repository root):
  python3 scripts/dashboard.py [WORKSPACE] [--port 8765] [--no-browser]
  (Windows: python scripts/dashboard.py)

Press Ctrl+C in the terminal to stop it.
"""

import argparse
import json
import mimetypes
import re
import secrets
import sys
import threading
import webbrowser
from datetime import date
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_dashboard  # noqa: E402
import tracker_schema as ts  # noqa: E402

EDITABLE = ("status", "next_step", "next_step_date", "notes")
LIMITS = {"next_step": 200, "notes": 2000}
SERVED_DIRS = ("cvs", "letters", "job_descriptions")
MAX_BODY = 20_000
_LOCK = threading.Lock()
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


class UpdateError(ValueError):
    """A save that breaks the rules; the message is shown to the user."""


def validate_update(payload: dict) -> dict:
    """The four user-owned fields from a save request, checked. Raises UpdateError."""
    if not isinstance(payload, dict):
        raise UpdateError("the request was not understood")
    if not ts.text(payload.get("role_key")).strip():
        raise UpdateError("no role was given")
    extra = set(payload) - {"role_key", *EDITABLE}
    if extra:
        raise UpdateError("only your status, next step, next-step date and notes can be changed")
    out = {}
    status = ts.text(payload.get("status")).strip() or "Not started"
    if status not in ts.STATUS_VALUES:
        raise UpdateError(f"'{status}' is not one of the status options")
    out["status"] = status
    when = ts.text(payload.get("next_step_date")).strip()
    if when and ts.parse_date(when) is None:
        raise UpdateError("the next-step date must be a real date (YYYY-MM-DD) or empty")
    out["next_step_date"] = when
    for key in ("next_step", "notes"):
        value = ts.text(payload.get(key)).replace("\r\n", "\n").strip()
        if _CONTROL.search(value):
            raise UpdateError(f"the {key.replace('_', ' ')} contains characters that can't be saved")
        if len(value) > LIMITS[key]:
            raise UpdateError(f"the {key.replace('_', ' ')} is longer than {LIMITS[key]} characters")
        out[key] = value
    return out


def next_version_path(folder: Path, today: str) -> Path:
    """career_tracker_<today>.json if none exists for today, else the next _vN."""
    highest = 0
    for p in folder.glob(f"career_tracker_{today}*.json"):
        m = re.fullmatch(rf"career_tracker_{re.escape(today)}(?:_v(\d+))?\.json", p.name)
        if m:
            highest = max(highest, int(m.group(1) or 1))
    name = f"career_tracker_{today}.json" if highest == 0 else f"career_tracker_{today}_v{highest + 1}.json"
    return folder / name


def apply_update(workspace: Path, payload: dict) -> dict:
    """Save one role's four fields as a new tracker version and rebuild its dashboard."""
    changes = validate_update(payload)
    with _LOCK:
        latest = ts.latest_tracker(workspace)
        if latest is None:
            raise UpdateError("no tracker data file was found in workspace/")
        data = ts.load(latest)
        role = next((r for r in data.get("roles") or [] if ts.text(r.get("role_key")) == ts.text(payload["role_key"])), None)
        if role is None:
            raise UpdateError("that role isn't in the latest tracker")
        role.update(changes)
        target = next_version_path(workspace, date.today().isoformat())
        data["version"] = target.stem.replace("career_tracker_", "")
        target.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
        build_dashboard.output_path(target).write_text(build_dashboard.build(data), encoding="utf-8")
    return {"ok": True, "version": data["version"], "role": {k: role.get(k, "") for k in EDITABLE}}


def make_handler(workspace: Path, token: str, port_box: dict):
    class Handler(BaseHTTPRequestHandler):
        server_version = "CareerPathfinder"

        def log_message(self, *args):  # keep the terminal quiet
            pass

        def _host_ok(self) -> bool:
            host = (self.headers.get("Host") or "").lower()
            return host in {f"127.0.0.1:{port_box['port']}", f"localhost:{port_box['port']}"}

        def _send(self, code: int, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def _json(self, code: int, obj: dict):
            self._send(code, json.dumps(obj).encode("utf-8"), "application/json")

        def do_GET(self):
            if not self._host_ok():
                return self._send(403, b"Forbidden", "text/plain")
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                latest = ts.latest_tracker(workspace)
                if latest is None:
                    return self._send(404, b"No tracker data file in workspace/ yet.", "text/plain; charset=utf-8")
                page = build_dashboard.build(ts.load(latest), editable=True, token=token)
                return self._send(200, page.encode("utf-8"), "text/html; charset=utf-8")
            parts = [p for p in path.split("/") if p]
            if len(parts) >= 2 and parts[0] in SERVED_DIRS:
                base = (workspace / parts[0]).resolve()
                target = (base / "/".join(parts[1:])).resolve()
                if target.is_file() and target.is_relative_to(base):
                    ctype = mimetypes.guess_type(target.name)[0] or "text/plain; charset=utf-8"
                    if target.suffix in (".md", ".tex", ".txt"):
                        ctype = "text/plain; charset=utf-8"
                    return self._send(200, target.read_bytes(), ctype)
            return self._send(404, b"Not found", "text/plain")

        def do_POST(self):
            if not self._host_ok() or self.path != "/api/update":
                return self._json(403, {"ok": False, "error": "not allowed"})
            if not secrets.compare_digest(self.headers.get("X-CP-Token") or "", token):
                return self._json(403, {"ok": False, "error": "this page is out of date; reload it"})
            origin = self.headers.get("Origin")
            if origin and origin not in {f"http://127.0.0.1:{port_box['port']}", f"http://localhost:{port_box['port']}"}:
                return self._json(403, {"ok": False, "error": "not allowed"})
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                return self._json(400, {"ok": False, "error": "the request was too large or empty"})
            try:
                payload = json.loads(self.rfile.read(length).decode("utf-8"))
                return self._json(200, apply_update(workspace, payload))
            except UpdateError as exc:
                return self._json(400, {"ok": False, "error": str(exc)})
            except (ValueError, OSError) as exc:
                return self._json(500, {"ok": False, "error": f"could not save ({type(exc).__name__})"})

    return Handler


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Open the dashboard on this computer with your own fields editable.")
    ap.add_argument("workspace", nargs="?", type=Path, default=HERE.parent / "workspace")
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--no-browser", action="store_true")
    args = ap.parse_args(argv)

    workspace = args.workspace.resolve()
    if ts.latest_tracker(workspace) is None:
        print(f"dashboard: no career_tracker_*.json in {workspace} yet. Run a search first.", file=sys.stderr)
        return 2
    token = secrets.token_urlsafe(32)
    port_box = {"port": args.port}
    try:
        server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(workspace, token, port_box))
    except OSError:
        server = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(workspace, token, port_box))
    port_box["port"] = server.server_address[1]
    url = f"http://127.0.0.1:{port_box['port']}/"
    print(f"Career Pathfinder dashboard: {url}\nOnly this computer can open it. Press Ctrl+C to stop.")
    if not args.no_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
