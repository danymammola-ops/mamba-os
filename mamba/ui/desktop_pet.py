#!/usr/bin/env python3
"""
mamba/ui/desktop_pet.py - Floating Desktop Snake Pet per Mamba OS
Un personaggetto fluttuante trasparente sullo schermo (stile Codex Mini & Pets),
posizionabile su qualsiasi app (WhatsApp, Spotify, Browser, Desktop).
"""

import sys
import os
import math
import time
import json
import tkinter as tk
from threading import Thread

# Palette colori per le diverse specie/skin del serpente
SKINS = {
    "emerald": {
        "name": "Emerald Viper",
        "primary": "#00ff88",
        "dark": "#042e1d",
        "body": "#064028",
        "eye": "#00ff88",
        "pupil": "#020b06",
        "tongue": "#00ffaa",
        "glow": "#00ff88"
    },
    "cyber": {
        "name": "Cyber Python",
        "primary": "#c77dff",
        "dark": "#240046",
        "body": "#3c096c",
        "eye": "#e0aaff",
        "pupil": "#10002b",
        "tongue": "#ff5400",
        "glow": "#c77dff"
    },
    "golden": {
        "name": "Golden Cobra",
        "primary": "#ffb703",
        "dark": "#3d2600",
        "body": "#5a3a00",
        "eye": "#ffe066",
        "pupil": "#1a1000",
        "tongue": "#ff0055",
        "glow": "#ffb703"
    },
    "crimson": {
        "name": "Crimson Mamba",
        "primary": "#ff0055",
        "dark": "#3a0014",
        "body": "#5c0022",
        "eye": "#ff5488",
        "pupil": "#1a0009",
        "tongue": "#ffbe0b",
        "glow": "#ff0055"
    },
    "mecha": {
        "name": "Mecha Robo-Snake",
        "primary": "#00f0ff",
        "dark": "#002b36",
        "body": "#003b46",
        "eye": "#00f0ff",
        "pupil": "#001015",
        "tongue": "#ff007f",
        "glow": "#00f0ff"
    }
}

CONFIG_FILE = os.path.join(os.path.dirname(__file__), "pet_config.json")

def load_config():
    default_cfg = {
        "enabled": True,
        "skin": "emerald",
        "show_on_all": True,
        "show_on_whatsapp": True,
        "show_on_spotify": True,
        "show_on_browser": True,
        "animated_tongue": True,
        "speaking_sway": True,
        "position_x": 60,
        "position_y": 780
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                default_cfg.update(cfg)
        except Exception:
            pass
    return default_cfg

def save_config(cfg):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

class DesktopSnakePet:
    def __init__(self):
        self.config = load_config()
        self.skin_key = self.config.get("skin", "emerald")
        self.skin = SKINS.get(self.skin_key, SKINS["emerald"])

        self.root = tk.Tk()
        self.root.title("Mamba Mini Pet")
        
        # Dimensioni finestra pet trasparente
        self.w = 140
        self.h = 140
        
        # Rendi la finestra senza bordi, sempre in primo piano e con sfondo trasparente
        self.root.overrideredirect(True)
        self.root.wm_attributes("-topmost", True)
        self.transparent_color = "#010101"
        self.root.wm_attributes("-transparentcolor", self.transparent_color)
        self.root.config(bg=self.transparent_color)

        # Posizionamento iniziale sullo schermo
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        init_x = self.config.get("position_x", 60)
        init_y = self.config.get("position_y", screen_h - self.h - 80)
        self.root.geometry(f"{self.w}x{self.h}+{init_x}+{init_y}")

        # Canvas grafico
        self.canvas = tk.Canvas(self.root, width=self.w, height=self.h, 
                               bg=self.transparent_color, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # Drag and drop con il mouse
        self._drag_data = {"x": 0, "y": 0}
        self.canvas.bind("<Button-1>", self.on_start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release_drag)
        self.canvas.bind("<Double-Button-1>", self.on_double_click)
        self.canvas.bind("<Enter>", self.on_hover_enter)
        self.canvas.bind("<Leave>", self.on_hover_leave)

        self.time_counter = 0
        self.is_hovered = False
        self.is_speaking = False
        self.sway_x = 0

        # Loop di animazione a 30 FPS
        self.animate()

    def set_skin(self, skin_name):
        if skin_name in SKINS:
            self.skin_key = skin_name
            self.skin = SKINS[skin_name]
            self.config["skin"] = skin_name
            save_config(self.config)

    def on_start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def on_drag(self, event):
        dx = event.x - self._drag_data["x"]
        dy = event.y - self._drag_data["y"]
        x = self.root.winfo_x() + dx
        y = self.root.winfo_y() + dy
        self.root.geometry(f"+{x}+{y}")

    def on_release_drag(self, event):
        self.config["position_x"] = self.root.winfo_x()
        self.config["position_y"] = self.root.winfo_y()
        save_config(self.config)

    def on_hover_enter(self, event):
        self.is_hovered = True

    def on_hover_leave(self, event):
        self.is_hovered = False

    def on_double_click(self, event):
        # Doppio click: apri Mamba OS App
        os.system("start http://127.0.0.1:5173")

    def animate(self):
        self.time_counter += 0.08
        self.canvas.delete("all")

        cx = self.w // 2
        cy = self.h // 2 + 10

        # 1. Movimento ondeggiante (sway)
        sway = 0
        if self.config.get("speaking_sway", True):
            if self.is_hovered or self.is_speaking:
                sway = math.sin(self.time_counter * 5) * 16
            else:
                sway = math.sin(self.time_counter * 1.5) * 6
        
        breathe = math.sin(self.time_counter * 2.5) * 3
        head_x = cx + sway
        head_y = cy + breathe

        # 2. Cappuccio Cobra posteriore (espansione)
        hood_w = 46 + (4 if self.is_hovered else 0)
        self.canvas.create_oval(
            head_x - hood_w, head_y - 25,
            head_x + hood_w, head_y + 35,
            fill=self.skin["dark"],
            outline=self.skin["primary"],
            width=2
        )

        # Dettagli del cappuccio (nervature olografiche)
        for dy in [-10, 5, 20]:
            spread = 32 - abs(dy) * 0.7
            self.canvas.create_line(
                head_x - spread, head_y + dy,
                head_x + spread, head_y + dy,
                fill=self.skin["primary"],
                width=1
            )

        # 3. Testa triangolare frontale
        points = [
            head_x, head_y - 34,        # Muso cima
            head_x + 24, head_y - 12,   # Lato destro alto
            head_x + 18, head_y + 16,   # Mascella destra
            head_x, head_y + 22,        # Mento
            head_x - 18, head_y + 16,   # Mascella sinistra
            head_x - 24, head_y - 12,   # Lato sinistro alto
        ]
        self.canvas.create_polygon(
            points,
            fill=self.skin["body"],
            outline=self.skin["primary"],
            width=2
        )

        # 4. Lingua biforcuta (flick animato)
        cycle = (self.time_counter % 4.0)
        if self.config.get("animated_tongue", True) and (cycle > 0.4 and cycle < 1.2 or self.is_hovered):
            flick = math.sin(self.time_counter * 30) * 4
            t_base_y = head_y + 22
            t_len = 20
            # Asta della lingua
            self.canvas.create_line(head_x, t_base_y, head_x + flick, t_base_y + t_len, 
                                    fill=self.skin["tongue"], width=2)
            # Due punte biforcute
            self.canvas.create_line(head_x + flick, t_base_y + t_len, head_x + flick - 6, t_base_y + t_len + 7, 
                                    fill=self.skin["tongue"], width=2)
            self.canvas.create_line(head_x + flick, t_base_y + t_len, head_x + flick + 6, t_base_y + t_len + 7, 
                                    fill=self.skin["tongue"], width=2)

        # 5. Occhi penetranti frontali
        blink = math.sin(self.time_counter * 0.5)
        is_blinking = blink > 0.95 and not self.is_hovered

        for side in [-1, 1]:
            ex = head_x + (side * 11)
            ey = head_y - 10
            
            if is_blinking:
                # Occhio chiuso
                self.canvas.create_line(ex - 4, ey, ex + 4, ey, fill=self.skin["primary"], width=2)
            else:
                # Occhio aperto a mandorla
                self.canvas.create_oval(ex - 5, ey - 7, ex + 5, ey + 7, 
                                        fill=self.skin["eye"], outline=self.skin["primary"], width=1)
                # Pupilla a fessura verticale da rettile
                self.canvas.create_oval(ex - 1.2, ey - 6, ex + 1.2, ey + 6, 
                                        fill=self.skin["pupil"], outline=self.skin["pupil"])
                # Punti luce brillanti
                self.canvas.create_oval(ex - 2, ey - 3, ex, ey - 1, fill="#ffffff", outline="#ffffff")

        # 6. Fumetto amichevole se mouse sopra (Hover Speech Bubble)
        if self.is_hovered:
            self.canvas.create_rectangle(
                head_x - 42, head_y - 62, head_x + 42, head_y - 42,
                fill=self.skin["dark"], outline=self.skin["primary"], width=1
            )
            self.canvas.create_text(
                head_x, head_y - 52,
                text="Sssono qui! 🐍", fill=self.skin["primary"],
                font=("Consolas", 8, "bold")
            )

        # Ripeti a ~30ms (33 fps)
        self.root.after(33, self.animate)

def start_pet():
    pet = DesktopSnakePet()
    pet.root.mainloop()

if __name__ == "__main__":
    start_pet()
