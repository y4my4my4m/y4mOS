#!/usr/bin/env python3
# Host-side clipboard bridge for the YKD network clipboard (Clip.ZC).
# Run on the QEMU HOST (Manjaro). The guest reaches it at 10.0.2.2:9999 via
# QEMU user-mode networking.
#
#   python3 clipd.py                 # binds 0.0.0.0:9999
#   python3 clipd.py 9999            # custom port
#
#   GET  /   -> returns the host clipboard (for guest -> ClipPull / Ctrl+V)
#   POST /   -> sets the host clipboard from the body (for guest -> ClipPush / Ctrl+C)
#
# Needs a clipboard tool:
#   Wayland:  pacman -S wl-clipboard      (wl-copy / wl-paste)
#   X11:      pacman -S xclip             (xclip)

import shutil
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# pick a clipboard backend once, at startup
if shutil.which("wl-copy") and shutil.which("wl-paste"):
    BACKEND = "wayland"
    GET_CMD = ["wl-paste", "-n"]
    SET_CMD = ["wl-copy"]
elif shutil.which("xclip"):
    BACKEND = "x11"
    GET_CMD = ["xclip", "-selection", "clipboard", "-o"]
    SET_CMD = ["xclip", "-selection", "clipboard"]
else:
    BACKEND = None


def clip_get():
    if not BACKEND:
        return b""
    try:
        return subprocess.check_output(GET_CMD)
    except Exception as e:
        print(f"  clip_get error: {e}")
        return b""


def clip_set(data):
    if not BACKEND:
        return False
    try:
        subprocess.run(SET_CMD, input=data, check=True)
        return True
    except Exception as e:
        print(f"  clip_set error: {e}")
        return False


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = clip_get()
        print(f"GET  -> sent {len(body)} bytes")
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        ok = clip_set(body)
        print(f"POST <- {n} bytes, set={'ok' if ok else 'FAILED'}: {body[:40]!r}")
        self.send_response(200 if ok else 500)
        self.end_headers()

    def log_message(self, *args):
        pass  # we print our own concise lines above


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    if BACKEND is None:
        print("WARNING: no clipboard tool found. Install one:")
        print("  Wayland:  sudo pacman -S wl-clipboard")
        print("  X11:      sudo pacman -S xclip")
        print("The bridge will still answer HTTP but can't touch your clipboard.")
    else:
        print(f"clipboard backend: {BACKEND}")
    print(f"YKD clipboard bridge on 0.0.0.0:{port} (guest -> http://10.0.2.2:{port})")
    print("Watching for guest requests (Ctrl+C to stop the daemon)...")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
