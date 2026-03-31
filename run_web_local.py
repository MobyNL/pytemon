#!/usr/bin/env python
"""
run_web_local.py — Serve pytemon in a browser via a local PTY WebSocket server.

Self-contained alternative to textual-web.  No cloud account, no Ganglion relay.
Uses aiohttp (already a transitive dependency) + xterm.js (loaded from CDN).

Usage:
    poetry run python run_web_local.py
    # then open http://localhost:7681 in your browser

How it works
------------
1.  aiohttp serves a single HTML page that embeds xterm.js.
2.  xterm.js opens a WebSocket to /ws.
3.  The /ws handler spawns the game in a PTY (pty.openpty) so Textual sees a
    real terminal and renders colours/layout correctly.
4.  PTY output → WebSocket binary frames → xterm.js renders in the browser.
5.  Keyboard input → WebSocket binary frames → PTY stdin.
6.  Terminal resize events → WebSocket JSON text frame → ioctl(TIOCSWINSZ).
"""

import asyncio
import fcntl
import json
import logging
import os
import pty
import struct
import subprocess
import termios
from pathlib import Path

from aiohttp import WSMsgType, web

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger(__name__)

PORT = 7681
GAME_CMD = ["poetry", "run", "python", "run_terminal.py"]
ROOT = Path(__file__).parent

# ---------------------------------------------------------------------------
# HTML page — xterm.js loaded from CDN; no local build step required
# ---------------------------------------------------------------------------
_HTML = """\
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>🎮 Pytemon Web</title>
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/xterm@5/css/xterm.css">
  <style>
    * { box-sizing: border-box; }
    html, body {
      margin: 0; padding: 0;
      background: #0d0d0d;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: stretch;
      font-family: sans-serif;
      color: #ccc;
    }
    h1 { margin: 0 0 4px; font-size: 1rem; letter-spacing: 2px; text-align: center; }
    #terminal-wrap {
      flex: 1;
      display: flex;
      align-items: stretch;
      padding: 0 8px 8px;
      min-height: 0;
    }
    #terminal { flex: 1; min-width: 0; }
  </style>
</head>
<body>
  <h1>🎮 PYTEMON — browser mode</h1>
  <div id="terminal-wrap">
    <div id="terminal"></div>
  </div>

  <script src="https://cdn.jsdelivr.net/npm/xterm@5/lib/xterm.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/xterm-addon-fit@0.8/lib/xterm-addon-fit.js"></script>
  <script>
    const term = new Terminal({
      cursorBlink: true,
      fontFamily: '"Cascadia Code", "Fira Code", "JetBrains Mono", monospace',
      fontSize: 14,
      theme: { background: '#0d0d0d' },
      allowTransparency: true,
    });
    const fitAddon = new FitAddon.FitAddon();
    term.loadAddon(fitAddon);
    term.open(document.getElementById('terminal'));
    fitAddon.fit();

    const ws = new WebSocket(`ws://${location.host}/ws`);
    ws.binaryType = 'arraybuffer';

    ws.onopen = () => {
      sendResize();
      term.focus();
    };

    ws.onmessage = (event) => {
      term.write(new Uint8Array(event.data));
    };

    ws.onclose = () => {
      term.write('\\r\\n\\r\\n[Connection closed — refresh to restart]\\r\\n');
    };

    // Keyboard → PTY (binary frame for correct UTF-8 handling)
    term.onData((data) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(new TextEncoder().encode(data));
      }
    });

    // Resize → PTY (JSON text frame so the server can distinguish it)
    function sendResize() {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'resize', cols: term.cols, rows: term.rows }));
      }
    }

    const ro = new ResizeObserver(() => { fitAddon.fit(); sendResize(); });
    ro.observe(document.getElementById('terminal-wrap'));
    term.onResize(() => sendResize());
  </script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# aiohttp handlers
# ---------------------------------------------------------------------------

async def handle_index(request: web.Request) -> web.Response:  # noqa: ARG001
    return web.Response(text=_HTML, content_type="text/html")


async def handle_ws(request: web.Request) -> web.WebSocketResponse:
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    log.info("Browser connected")

    master_fd, slave_fd = pty.openpty()
    _set_winsize(master_fd, cols=220, rows=50)  # sensible default before first resize

    proc = subprocess.Popen(  # noqa: S603
        GAME_CMD,
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        close_fds=True,
        cwd=str(ROOT),
    )
    os.close(slave_fd)
    log.info("Game started  pid=%d", proc.pid)

    loop = asyncio.get_running_loop()

    async def _pty_to_ws() -> None:
        """Forward PTY output → WebSocket binary frames (non-blocking via add_reader)."""
        while True:
            fut: asyncio.Future[bytes] = loop.create_future()

            def _readable() -> None:
                loop.remove_reader(master_fd)
                if fut.done():
                    return
                try:
                    fut.set_result(os.read(master_fd, 4096))
                except OSError as exc:
                    fut.set_exception(exc)

            loop.add_reader(master_fd, _readable)
            try:
                data = await fut
                if data:
                    await ws.send_bytes(data)
            except OSError:
                break

    reader_task = asyncio.create_task(_pty_to_ws())

    async for msg in ws:
        if msg.type == WSMsgType.BINARY:
            # Keyboard input from xterm.js
            try:
                os.write(master_fd, msg.data)
            except OSError:
                break
        elif msg.type == WSMsgType.TEXT:
            # Control message (currently only resize)
            try:
                ctrl = json.loads(msg.data)
                if ctrl.get("type") == "resize":
                    _set_winsize(master_fd, cols=int(ctrl["cols"]), rows=int(ctrl["rows"]))
            except (json.JSONDecodeError, KeyError, ValueError):
                pass
        elif msg.type in (WSMsgType.ERROR, WSMsgType.CLOSE):
            break

    reader_task.cancel()
    try:
        proc.terminate()
    except ProcessLookupError:
        pass
    try:
        loop.remove_reader(master_fd)
        os.close(master_fd)
    except OSError:
        pass
    log.info("Browser disconnected  pid=%d", proc.pid)
    return ws


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _set_winsize(fd: int, cols: int, rows: int) -> None:
    """Send TIOCSWINSZ to the PTY master — triggers SIGWINCH in the child."""
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", rows, cols, 0, 0))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    app = web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/ws", handle_ws)

    print()
    print("  🌐  Pytemon browser mode")
    print(f"      http://localhost:{PORT}")
    print()
    print("  Open the URL above in your browser to play.")
    print("  Each browser tab launches a fresh game session.")
    print("  Press Ctrl+C here to stop the server.")
    print()

    web.run_app(app, host="localhost", port=PORT, print=lambda *_: None)


if __name__ == "__main__":
    main()
