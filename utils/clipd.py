#!/usr/bin/env python3
# Host-side clipboard bridge for the y4mOS network clipboard (Clip.ZC).
# Run on the QEMU HOST (Manjaro). The guest reaches it at 10.0.2.2:9999 via
# QEMU user-mode networking.
#
#   python3 clipd.py                 # binds 0.0.0.0:9999
#   python3 clipd.py 9999            # custom port
#
#   GET  /   -> returns the host clipboard (for guest ClipPaste)
#   POST /   -> sets the host clipboard from the body (for guest ClipCopy)
#
# Uses wl-copy/wl-paste (Wayland) and falls back to xclip (X11).
# Manjaro: `pacman -S wl-clipboard` (Wayland) or `xclip` (X11).

import subprocess
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer


def clip_get():
    for cmd in (["wl-paste", "-n"], ["xclip", "-selection", "clipboard", "-o"]):
        try:
            return subprocess.check_output(cmd)
        except Exception:
            continue
    return b""


def clip_set(data):
    for cmd in (["wl-copy"], ["xclip", "-selection", "clipboard"]):
        try:
            subprocess.run(cmd, input=data, check=True)
            return True
        except Exception:
            continue
    return False


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = clip_get()
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        ok = clip_set(body)
        self.send_response(200 if ok else 500)
        self.end_headers()

    def log_message(self, *args):
        pass  # quiet


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 9999
    print(f"y4mOS clipboard bridge on 0.0.0.0:{port} (guest -> http://10.0.2.2:{port})")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
