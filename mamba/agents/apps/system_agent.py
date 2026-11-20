#!/usr/bin/env python3
"""
mamba/agents/apps/system_agent.py - Micro-Agente Specialista Sistema & Finestre per Mamba OS
Gestisce:
- Chiusura rapida di app (Spotify, etc.)
- Window Snapping a metà schermo (50/50, Meet, Browser, etc.)
- Controllo processi Windows
"""

import time
import sys
import os
import ctypes
import subprocess
import pyautogui

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size
)

attach_to_user_desktop()
import uiautomation as auto

class SystemAgent:
    def __init__(self):
        attach_to_user_desktop()
        self.user32 = ctypes.windll.user32

    def close_app(self, app_name: str) -> dict:
        """Chiude un'applicazione per nome finestra o processo (es. Spotify)."""
        attach_to_user_desktop()
        print(f"🪟 [SYSTEM AGENT] Chiusura applicazione: '{app_name}'...")
        app_lower = app_name.lower()
        closed_windows = 0

        root = auto.GetRootControl()
        for child in root.GetChildren():
            name = (child.Name or "").lower()
            cls = (child.ClassName or "").lower()
            if app_lower in name or app_lower in cls:
                hwnd = child.NativeWindowHandle
                print(f" -> Invio WM_CLOSE a HWND {hwnd} ('{child.Name}')...")
                self.user32.PostMessageW(hwnd, 0x0010, 0, 0)
                closed_windows += 1

        time.sleep(0.5)
        # Forza la chiusura del processo se ancora attivo
        subprocess.run(["powershell", "-Command", f"Stop-Process -Name '{app_name}' -Force -ErrorAction SilentlyContinue"], capture_output=True)
        print(f"✅ [SYSTEM AGENT] Applicazione '{app_name}' chiusa.")
        return {"success": True, "app": app_name, "windows_closed": closed_windows}

    def snap_window(self, window_keyword: str, direction: str = "left", percent: int = 50) -> dict:
        """
        Aggancia una finestra e la ridimensiona al 50% dello schermo (es. 'meet', 'zen', 'chrome').
        NON la chiude mai!
        """
        attach_to_user_desktop()
        screen_w, screen_h = get_screen_size()
        print(f"🪟 [SYSTEM AGENT] Snapping finestra '{window_keyword}' a {direction} ({percent}%)...")

        root = auto.GetRootControl()
        target = None
        for child in root.GetChildren():
            name = (child.Name or "").lower()
            if window_keyword.lower() in name:
                target = child
                break

        if not target:
            return {"success": False, "error": f"Nessuna finestra trovata per '{window_keyword}'"}

        hwnd = target.NativeWindowHandle
        self.user32.ShowWindow(hwnd, 9) # RESTORE
        time.sleep(0.2)
        self.user32.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        # Snap nativo con hotkey Windows
        hotkey_dir = 'left' if direction == 'left' else 'right'
        pyautogui.hotkey('win', hotkey_dir)
        time.sleep(0.4)
        pyautogui.press('esc')
        time.sleep(0.2)

        rect = target.BoundingRectangle
        print(f"✅ [SYSTEM AGENT] Finestra '{target.Name}' posizionata a {rect.width()}x{rect.height()} at ({rect.left}, {rect.top})")
        return {"success": True, "window": target.Name, "rect": (rect.left, rect.top, rect.width(), rect.height())}

if __name__ == "__main__":
    agent = SystemAgent()
    print("SystemAgent pronto.")
