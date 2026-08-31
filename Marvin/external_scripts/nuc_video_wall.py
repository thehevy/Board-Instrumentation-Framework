#!/usr/bin/env python3
"""NUC 2x2 video wall for up to four network streams.

Designed for demo use on the Windows NUC (or Linux) using VLC as the decode backend.
Requires:
  - VLC media player installed
  - pip install python-vlc

Examples:
  python scripts/nuc_video_wall.py --stream udp://@0.0.0.0:5000 --stream udp://@0.0.0.0:5001 --stream udp://@0.0.0.0:5002 --stream udp://@0.0.0.0:5003
  python scripts/nuc_video_wall.py --stream http://10.165.176.74:8080/lag1.m3u8 --stream http://10.165.176.74:8080/lag2.m3u8
"""

from __future__ import annotations

import argparse
import math
import platform
import sys
import tkinter as tk
from dataclasses import dataclass
from tkinter import messagebox

try:
    import vlc  # type: ignore
except Exception as exc:
    print("ERROR: python-vlc import failed. Install with: pip install python-vlc", file=sys.stderr)
    raise

MAX_STREAMS = 16


def default_streams(count: int, base_port: int = 5000) -> list[str]:
    return [f"udp://@0.0.0.0:{base_port + i}" for i in range(count)]


@dataclass
class StreamPanel:
    container: tk.Frame
    player: "vlc.MediaPlayer"
    title_var: tk.StringVar
    status_var: tk.StringVar
    uri: str


class VideoWallApp:
    def __init__(self, uris: list[str], wall_title: str, net_caching: int = 300,
                 fullscreen: bool = False) -> None:
        self.all_uris = uris[:MAX_STREAMS]
        self.uris = list(self.all_uris)
        self.root = tk.Tk()
        self.root.title(wall_title)
        self.root.configure(bg="#0d1117")
        self.root.geometry("1600x900")
        self.root.minsize(1200, 700)
        if fullscreen:
            self.root.attributes("-fullscreen", True)
        self.root.bind("<F11>", lambda e: self.root.attributes(
            "-fullscreen", not self.root.attributes("-fullscreen")))
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))

        self.instance = vlc.Instance("--no-video-title-show",
                                     f"--network-caching={net_caching}")
        self.panels: list[StreamPanel] = []
        self.main_frame: tk.Frame | None = None
        self.subtitle_var = tk.StringVar()
        self.count_var = tk.IntVar(value=len(self.uris))

        self._build_header(wall_title)
        self._build_grid()

        # Ensure embed targets exist before binding VLC players.
        self.root.update_idletasks()
        self.root.update()

        self._start_players()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_header(self, wall_title: str) -> None:
        header = tk.Frame(self.root, bg="#111827", padx=16, pady=10)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text=wall_title,
            font=("Segoe UI", 16, "bold"),
            fg="#e5e7eb",
            bg="#111827",
        )
        title.pack(side="left")

        subtitle = tk.Label(
            header,
            textvariable=self.subtitle_var,
            font=("Segoe UI", 11),
            fg="#9ca3af",
            bg="#111827",
        )
        subtitle.pack(side="left", padx=(12, 0))

        controls = tk.Frame(header, bg="#111827")
        controls.pack(side="right")

        tk.Label(
            controls,
            text="Videos:",
            font=("Segoe UI", 11),
            fg="#9ca3af",
            bg="#111827",
        ).pack(side="left", padx=(0, 4))

        count_menu = tk.OptionMenu(
            controls,
            self.count_var,
            *range(1, len(self.all_uris) + 1),
            command=self._on_count_change,
        )
        count_menu.configure(bg="#374151", fg="white", activebackground="#4b5563",
                             relief="flat", highlightthickness=0, width=3)
        count_menu["menu"].configure(bg="#111827", fg="white")
        count_menu.pack(side="left", padx=6)

        tk.Button(
            controls,
            text="Reload",
            command=self.reload_all,
            bg="#2563eb",
            fg="white",
            activebackground="#1d4ed8",
            relief="flat",
            padx=12,
            pady=4,
        ).pack(side="left", padx=6)

        tk.Button(
            controls,
            text="Pause/Play",
            command=self.toggle_pause_all,
            bg="#374151",
            fg="white",
            activebackground="#4b5563",
            relief="flat",
            padx=12,
            pady=4,
        ).pack(side="left", padx=6)

    def _build_grid(self) -> None:
        main = tk.Frame(self.root, bg="#0d1117", padx=12, pady=12)
        main.pack(fill="both", expand=True)
        self.main_frame = main

        n = len(self.uris)
        self.subtitle_var.set(f"{n}-stream RDMA LAG demo view")
        cols = math.ceil(math.sqrt(n)) if n else 1
        rows = math.ceil(n / cols) if n else 1

        for r in range(rows):
            main.grid_rowconfigure(r, weight=1, uniform="row")
        for c in range(cols):
            main.grid_columnconfigure(c, weight=1, uniform="col")

        for idx in range(n):
            row = idx // cols
            col = idx % cols
            uri = self.uris[idx]
            panel = self._create_panel(main, idx + 1, uri)
            panel.container.grid(row=row, column=col, padx=6, pady=6, sticky="nsew")
            self.panels.append(panel)

    def _on_count_change(self, value) -> None:
        count = int(value)
        if count == len(self.panels):
            return
        self._stop_players()
        if self.main_frame is not None:
            self.main_frame.destroy()
        self.panels = []
        self.uris = self.all_uris[:count]
        self._build_grid()
        self.root.update_idletasks()
        self.root.update()
        self._start_players()

    def _stop_players(self) -> None:
        for panel in self.panels:
            try:
                panel.player.stop()
                panel.player.release()
            except Exception:
                pass

    def _create_panel(self, parent: tk.Widget, stream_num: int, uri: str) -> StreamPanel:
        outer = tk.Frame(parent, bg="#111827", highlightthickness=1, highlightbackground="#1f2937")

        top = tk.Frame(outer, bg="#111827")
        top.pack(fill="x", padx=8, pady=(8, 4))

        title_var = tk.StringVar(value=f"LAG Stream {stream_num}")
        status_var = tk.StringVar(value="Idle" if uri else "No URI configured")

        tk.Label(
            top,
            textvariable=title_var,
            font=("Segoe UI", 11, "bold"),
            fg="#e5e7eb",
            bg="#111827",
        ).pack(side="left")

        tk.Label(
            top,
            textvariable=status_var,
            font=("Segoe UI", 9),
            fg="#9ca3af",
            bg="#111827",
        ).pack(side="right")

        video_frame = tk.Frame(outer, bg="black")
        video_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        player = self.instance.media_player_new()
        return StreamPanel(container=outer, player=player, title_var=title_var, status_var=status_var, uri=uri)

    def _bind_player_to_frame(self, player: "vlc.MediaPlayer", frame: tk.Frame) -> None:
        handle = frame.winfo_id()
        system = platform.system().lower()
        if "windows" in system:
            player.set_hwnd(handle)
        elif "linux" in system:
            player.set_xwindow(handle)
        elif "darwin" in system:
            player.set_nsobject(handle)

    def _start_players(self) -> None:
        for panel in self.panels:
            # Video frame is the second child (after panel top bar).
            video_frame = panel.container.winfo_children()[1]
            self._bind_player_to_frame(panel.player, video_frame)  # type: ignore[arg-type]

            if not panel.uri:
                panel.status_var.set("No URI configured")
                continue

            media = self.instance.media_new(panel.uri)
            panel.player.set_media(media)
            rc = panel.player.play()
            if rc == -1:
                panel.status_var.set("Play failed")
            else:
                panel.status_var.set("Playing")

    def reload_all(self) -> None:
        for panel in self.panels:
            if not panel.uri:
                continue
            panel.player.stop()
            media = self.instance.media_new(panel.uri)
            panel.player.set_media(media)
            rc = panel.player.play()
            panel.status_var.set("Playing" if rc != -1 else "Play failed")

    def toggle_pause_all(self) -> None:
        for panel in self.panels:
            if panel.uri:
                panel.player.pause()

    def _on_close(self) -> None:
        for panel in self.panels:
            try:
                panel.player.stop()
                panel.player.release()
            except Exception:
                pass
        try:
            self.instance.release()
        except Exception:
            pass
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NUC video wall (dynamic grid, up to 16 streams)")
    parser.add_argument(
        "--stream",
        action="append",
        default=[],
        help="Stream URI (repeat up to 16 times). Example: --stream udp://@0.0.0.0:5000",
    )
    parser.add_argument(
        "--title",
        default="Intel E835 RDMA LAG Demo - NUC Video Wall",
        help="Window title",
    )
    parser.add_argument(
        "--use-default-ports",
        action="store_true",
        help="Use udp://@0.0.0.0:<base_port>..(base_port+count-1) when no --stream values are passed",
    )
    parser.add_argument(
        "--count", type=int, default=10,
        help="Number of default UDP streams to make available (default: 10)",
    )
    parser.add_argument(
        "--base-port", type=int, default=5000,
        help="Base UDP port for default streams (default: 5000)",
    )
    parser.add_argument(
        "--net-caching", type=int, default=300,
        help="VLC network caching in ms; raise to reduce jitter, lower for latency (default: 300)",
    )
    parser.add_argument(
        "--fullscreen", action="store_true", help="Start in fullscreen (toggle F11, exit Esc)",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.stream:
        streams = args.stream[:MAX_STREAMS]
    elif args.use_default_ports:
        streams = default_streams(max(1, min(args.count, MAX_STREAMS)), args.base_port)
    else:
        streams = []

    if not streams:
        # Keep UX simple: show exactly what to do when no URIs are supplied.
        msg = (
            "No stream URIs provided.\n\n"
            "Examples:\n"
            "  python scripts/nuc_video_wall.py --use-default-ports --count 10\n"
            "  python scripts/nuc_video_wall.py --stream udp://@0.0.0.0:5000 --stream udp://@0.0.0.0:5001\n"
        )
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("NUC Video Wall", msg)
        root.destroy()
        return 2

    app = VideoWallApp(uris=streams, wall_title=args.title,
                       net_caching=args.net_caching, fullscreen=args.fullscreen)
    app.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
