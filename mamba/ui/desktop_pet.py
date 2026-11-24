#!/usr/bin/env python3
"""
mamba/ui/desktop_pet.py - Codex-Style Configurable Floating Pixel Snake Pet
Caratteristiche:
- Single-instance garantita tramite pet.pid
- Hot-reload live di pet_config.json (skin, stile pixel/classic, dimensione, opacità, visibilità app)
- Rilevamento reale finestra attiva Windows (WhatsApp, Spotify, Browser, Notepad, VS Code, Obsidian)
- Stile Pixel-Art nitido con coda/movimento, lingua biforcuta, blink e fumetto al passaggio
"""

from __future__ import annotations

import ctypes
import json
import math
import os
import sys
import time
import tkinter as tk
from pathlib import Path

SKINS = {
    "emerald": {"name": "Emerald Viper", "primary": "#00ff88", "mid": "#059669", "dark": "#032617", "eye": "#eafff5", "pupil": "#020b06", "tongue": "#00ffaa"},
    "cyber":   {"name": "Cyber Python",  "primary": "#c77dff", "mid": "#7b2cbf", "dark": "#240046", "eye": "#f3e8ff", "pupil": "#10002b", "tongue": "#ff5400"},
    "golden":  {"name": "Golden Cobra",  "primary": "#ffb703", "mid": "#d97706", "dark": "#3d2600", "eye": "#fef9c3", "pupil": "#1a1000", "tongue": "#ff0055"},
    "crimson": {"name": "Crimson Mamba", "primary": "#ff2a6d", "mid": "#be123c", "dark": "#3a0014", "eye": "#ffe4e6", "pupil": "#1a0009", "tongue": "#ffbe0b"},
    "mecha":   {"name": "Mecha Robo",    "primary": "#00f0ff", "mid": "#0284c7", "dark": "#002b36", "eye": "#e0f2fe", "pupil": "#001015", "tongue": "#ff007f"},
}

SIZES = {"small": 96, "medium": 136, "large": 176}

UI_DIR = Path(__file__).resolve().parent
CONFIG_FILE = UI_DIR / "pet_config.json"
PID_FILE = UI_DIR / "pet.pid"

DEFAULT_CFG = {
    "enabled": True,
    "skin": "emerald",
    "style": "pixel",        # "pixel" | "classic"
    "size": "medium",        # "small" | "medium" | "large"
    "opacity": 0.96,
    "show_on_all": True,
    "show_on_desktop": True,
    "show_on_whatsapp": True,
    "show_on_spotify": True,
    "show_on_browser": True,
    "show_on_notepad": True,
    "show_on_vscode": True,
    "show_on_obsidian": True,
    "animated_tongue": True,
    "speaking_sway": True,
    "slither_idle": True,
    "bubble_enabled": True,
    "position_x": 48,
    "position_y": 720,
    "wave_until": 0.0,
}

# Griglia 16x16 Pixel-Art Cobra Mamba (0=vuoto, 1=dark, 2=mid, 3=primary, 4=eye, 5=pupil)
PIXEL_COBRA_16 = [
    "0000003333000000",
    "0000332222330000",
    "0003221111223000",
    "0032113333112300",
    "0321322222231230",
    "0321244224421230",
    "0321245225421230",
    "0321222332221230",
    "0032122222212300",
    "0003211331123000",
    "0000321221230000",
    "0003212332123000",
    "0032122112212300",
    "0032112222112300",
    "0003322112233000",
    "0000033333300000",
]


def load_config() -> dict:
    cfg = dict(DEFAULT_CFG)
    if CONFIG_FILE.exists():
        try:
            data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                cfg.update(data)
        except Exception:
            pass
    return cfg


def save_config(cfg: dict) -> None:
    try:
        CONFIG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception:
        pass


def get_active_window_title() -> str:
    try:
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return ""
        length = user32.GetWindowTextLengthW(hwnd)
        if length <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buf, length + 1)
        return buf.value.lower()
    except Exception:
        return ""


class DesktopSnakePet:
    def __init__(self):
        self.config = load_config()
        self.last_cfg_mtime = CONFIG_FILE.stat().st_mtime if CONFIG_FILE.exists() else 0.0
        self.skin_key = self.config.get("skin", "emerald")
        self.skin = SKINS.get(self.skin_key, SKINS["emerald"])
        self.size_px = SIZES.get(self.config.get("size", "medium"), 136)

        self.root = tk.Tk()
        self.root.title("Mamba Mini Pet")
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.transparent_color = "#010101"
        self.root.wm_attributes("-transparentcolor", self.transparent_color)
        self.root.config(bg=self.transparent_color)
        self.root.wm_attributes("-alpha", float(self.config.get("opacity", 0.96)))

        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        init_x = min(max(0, int(self.config.get("position_x", 48))), max(0, screen_w - self.size_px))
        init_y = min(max(0, int(self.config.get("position_y", screen_h - self.size_px - 80))), max(0, screen_h - self.size_px))
        self.root.geometry(f"{self.size_px}x{self.size_px}+{init_x}+{init_y}")

        self.canvas = tk.Canvas(
            self.root, width=self.size_px, height=self.size_px,
            bg=self.transparent_color, highlightthickness=0,
        )
        self.canvas.pack(fill="both", expand=True)

        self._drag = {"x": 0, "y": 0}
        self.canvas.bind("<Button-1>", self._start_drag)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._end_drag)
        self.canvas.bind("<Double-Button-1>", lambda _e: os.system("start http://127.0.0.1:5173"))
        self.canvas.bind("<Enter>", lambda _e: setattr(self, "is_hovered", True))
        self.canvas.bind("<Leave>", lambda _e: setattr(self, "is_hovered", False))
        self.canvas.bind("<Button-3>", self._show_menu)

        self.menu = tk.Menu(self.root, tearoff=0, bg="#08131d", fg="#00ff88", activebackground="#00ff88", activeforeground="#03060a")
        self.menu.add_command(label="🐍 Apri Mamba HUD", command=lambda: os.system("start http://127.0.0.1:5173"))
        self.menu.add_command(label="🌌 Apri Galaxy 3D", command=lambda: os.system("start http://127.0.0.1:5173/galaxy.html"))
        self.menu.add_command(label="👋 Saluta!", command=self._trigger_wave)
        self.menu.add_separator()
        self.menu.add_command(label="✕ Nascondi Pet", command=self._disable_and_quit)

        self.t = 0.0
        self.is_hovered = False
        self.visible = True
        self.last_check = 0.0

        self._write_pid()
        self.animate()

    def _write_pid(self) -> None:
        try:
            PID_FILE.write_text(str(os.getpid()), encoding="utf-8")
        except Exception:
            pass

    def _trigger_wave(self) -> None:
        self.config["wave_until"] = time.time() + 2.5
        save_config(self.config)

    def _disable_and_quit(self) -> None:
        self.config["enabled"] = False
        save_config(self.config)
        self._cleanup_and_exit()

    def _cleanup_and_exit(self) -> None:
        try:
            if PID_FILE.exists() and PID_FILE.read_text(encoding="utf-8").strip() == str(os.getpid()):
                PID_FILE.unlink()
        except Exception:
            pass
        self.root.destroy()
        sys.exit(0)

    def _show_menu(self, event) -> None:
        try:
            self.menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.menu.grab_release()

    def _start_drag(self, event) -> None:
        self._drag = {"x": event.x, "y": event.y}

    def _on_drag(self, event) -> None:
        x = self.root.winfo_x() + (event.x - self._drag["x"])
        y = self.root.winfo_y() + (event.y - self._drag["y"])
        self.root.geometry(f"+{x}+{y}")

    def _end_drag(self, _event) -> None:
        self.config["position_x"] = self.root.winfo_x()
        self.config["position_y"] = self.root.winfo_y()
        save_config(self.config)

    def _hot_reload_and_visibility(self) -> None:
        now = time.time()
        if now - self.last_check < 0.35:
            return
        self.last_check = now

        # Hot reload config
        if CONFIG_FILE.exists():
            try:
                mt = CONFIG_FILE.stat().st_mtime
                if abs(mt - self.last_cfg_mtime) > 1e-4:
                    self.last_cfg_mtime = mt
                    new_cfg = load_config()
                    old_size = self.size_px
                    self.config = new_cfg

                    if not self.config.get("enabled", True):
                        self._cleanup_and_exit()
                        return

                    self.skin_key = self.config.get("skin", "emerald")
                    self.skin = SKINS.get(self.skin_key, SKINS["emerald"])
                    self.size_px = SIZES.get(self.config.get("size", "medium"), 136)
                    self.root.wm_attributes("-alpha", float(self.config.get("opacity", 0.96)))

                    if self.size_px != old_size or self.config.get("recenter"):
                        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
                        nx = int(self.config.get("position_x", 48))
                        ny = int(self.config.get("position_y", sh - self.size_px - 80))
                        if self.config.get("recenter"):
                            nx, ny = sw // 2 - self.size_px // 2, sh // 2 - self.size_px // 2
                            self.config["recenter"] = False
                            self.config["position_x"] = nx
                            self.config["position_y"] = ny
                            save_config(self.config)
                        self.canvas.config(width=self.size_px, height=self.size_px)
                        self.root.geometry(f"{self.size_px}x{self.size_px}+{nx}+{ny}")
            except Exception:
                pass

        # App visibility check
        if self.config.get("show_on_all", True):
            should_show = True
        else:
            title = get_active_window_title()
            should_show = self.config.get("show_on_desktop", True)
            app_rules = [
                ("whatsapp", "show_on_whatsapp"),
                ("spotify", "show_on_spotify"),
                ("chrome", "show_on_browser"),
                ("edge", "show_on_browser"),
                ("meet", "show_on_browser"),
                ("notepad", "show_on_notepad"),
                ("blocco note", "show_on_notepad"),
                ("visual studio code", "show_on_vscode"),
                ("obsidian", "show_on_obsidian"),
            ]
            for kw, key in app_rules:
                if kw in title:
                    should_show = bool(self.config.get(key, True))
                    break

        if should_show and not self.visible:
            self.root.deiconify()
            self.visible = True
        elif not should_show and self.visible:
            self.root.withdraw()
            self.visible = False

    def _draw_pixel_pet(self, ox: float, oy: float) -> None:
        w = self.size_px
        px = max(3, int((w * 0.62) / 16))
        start_x = ox - (16 * px) / 2
        start_y = oy - (16 * px) / 2

        is_blinking = (math.sin(self.t * 0.7) > 0.96) and not self.is_hovered
        palette = {
            "1": self.skin["dark"],
            "2": self.skin["mid"],
            "3": self.skin["primary"],
            "4": self.skin["primary"] if is_blinking else self.skin["eye"],
            "5": self.skin["primary"] if is_blinking else self.skin["pupil"],
        }

        for r, row in enumerate(PIXEL_COBRA_16):
            for c, ch in enumerate(row):
                if ch == "0":
                    continue
                x0 = start_x + c * px
                y0 = start_y + r * px
                self.canvas.create_rectangle(x0, y0, x0 + px, y0 + px, fill=palette[ch], outline="")

        # Lingua pixelata biforcuta
        waving = time.time() < float(self.config.get("wave_until", 0.0))
        if self.config.get("animated_tongue", True) and ((self.t % 3.6) < 0.9 or self.is_hovered or waving):
            tx = ox - px // 2
            ty = start_y + 15 * px
            flick = px if int(self.t * 14) % 2 == 0 else 0
            tc = self.skin["tongue"]
            self.canvas.create_rectangle(tx, ty, tx + px, ty + px * 2, fill=tc, outline="")
            self.canvas.create_rectangle(tx - px + flick // 2, ty + px * 2, tx, ty + px * 3, fill=tc, outline="")
            self.canvas.create_rectangle(tx + px + flick // 2, ty + px * 2, tx + px * 2, ty + px * 3, fill=tc, outline="")

    def _draw_classic_pet(self, cx: float, cy: float) -> None:
        s = self.size_px / 140.0
        self.canvas.create_oval(cx - 44 * s, cy - 26 * s, cx + 44 * s, cy + 32 * s, fill=self.skin["dark"], outline=self.skin["primary"], width=2)
        pts = [cx, cy - 32 * s, cx + 22 * s, cy - 10 * s, cx + 16 * s, cy + 16 * s, cx, cy + 22 * s, cx - 16 * s, cy + 16 * s, cx - 22 * s, cy - 10 * s]
        self.canvas.create_polygon(pts, fill=self.skin["mid"], outline=self.skin["primary"], width=2)
        for side in (-1, 1):
            ex, ey = cx + side * 10 * s, cy - 9 * s
            self.canvas.create_oval(ex - 4 * s, ey - 6 * s, ex + 4 * s, ey + 6 * s, fill=self.skin["eye"], outline=self.skin["primary"])
            self.canvas.create_oval(ex - 1 * s, ey - 5 * s, ex + 1 * s, ey + 5 * s, fill=self.skin["pupil"], outline="")

    def animate(self) -> None:
        self._hot_reload_and_visibility()
        self.t += 0.09
        if self.visible:
            self.canvas.delete("all")
            waving = time.time() < float(self.config.get("wave_until", 0.0))
            sway = 0.0
            if self.config.get("speaking_sway", True):
                if self.is_hovered or waving:
                    sway = math.sin(self.t * 6.0) * (self.size_px * 0.11)
                elif self.config.get("slither_idle", True):
                    sway = math.sin(self.t * 1.8) * (self.size_px * 0.04)

            bob = math.sin(self.t * 2.5) * 3.0
            cx = self.size_px / 2 + sway
            cy = self.size_px / 2 + 6 + bob

            if self.config.get("style", "pixel") == "classic":
                self._draw_classic_pet(cx, cy)
            else:
                self._draw_pixel_pet(cx, cy)

            if (self.is_hovered or waving) and self.config.get("bubble_enabled", True):
                msg = "Sssaluto! 🐍" if waving else "Sssono qui!"
                self.canvas.create_rectangle(
                    max(4, cx - 38), max(2, cy - self.size_px * 0.42),
                    min(self.size_px - 4, cx + 38), max(18, cy - self.size_px * 0.42 + 16),
                    fill=self.skin["dark"], outline=self.skin["primary"], width=1,
                )
                self.canvas.create_text(
                    cx, max(10, cy - self.size_px * 0.42 + 8),
                    text=msg, fill=self.skin["primary"], font=("Consolas", 8, "bold"),
                )

        self.root.after(33, self.animate)


if __name__ == "__main__":
    DesktopSnakePet().root.mainloop()
