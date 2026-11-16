#!/usr/bin/env python3
"""
mamba/moves/user_moves.py - Desktop Automation & Computer Use per Mamba OS
Controlla mouse, tastiera e cattura visiva con movimenti fluidi e naturali.

Supporta:
- Aggancio trasparente al desktop interattivo dell'utente (WinSta0\\default)
- Movimento fluido e visibile del mouse (smooth Bézier/ease-in-out)
- Click sinistro, destro, doppio click
- Digitazione naturale
- Cattura screenshot a schermo intero
"""

import time
import math
import os
import sys
import ctypes
from typing import Tuple, Optional, Dict, Any
from PIL import ImageGrab

# Strutture Win32
class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

def attach_to_user_desktop() -> bool:
    """
    Collega il thread Python corrente al desktop grafico attivo dell'utente (WinSta0\\default).
    Necessario su Windows se il processo viene avviato da agenti o terminali in background.
    """
    if sys.platform != "win32":
        return True
    try:
        user32 = ctypes.windll.user32
        hwinsta = user32.OpenWindowStationA(b"WinSta0", False, 0x00020000 | 0x037F)
        if hwinsta:
            user32.SetProcessWindowStation(hwinsta)
            hdesk = user32.OpenDesktopA(b"default", 0, False, 0x01FF)
            if hdesk:
                user32.SetThreadDesktop(hdesk)
                return True
    except Exception as e:
        print(f"[user_moves] Avviso aggancio desktop: {e}")
    return False

# Inizializza l'aggancio
attach_to_user_desktop()

try:
    import pyautogui
    pyautogui.PAUSE = 0.05
    pyautogui.FAILSAFE = False
except ImportError:
    pyautogui = None

def get_screen_size() -> Tuple[int, int]:
    """Restituisce (larghezza, altezza) dello schermo in pixel."""
    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        w = user32.GetSystemMetrics(0)
        h = user32.GetSystemMetrics(1)
        if w > 0 and h > 0:
            return (w, h)
    if pyautogui:
        s = pyautogui.size()
        return (s.width, s.height)
    return (1920, 1080)

def get_mouse_position() -> Tuple[int, int]:
    """Restituisce le coordinate attuali del mouse (x, y) sul desktop visibile."""
    attach_to_user_desktop()
    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        pt = POINT()
        if user32.GetCursorPos(ctypes.byref(pt)):
            return (pt.x, pt.y)
    if pyautogui:
        p = pyautogui.position()
        return (p.x, p.y)
    return (0, 0)

def smooth_move(target_x: int, target_y: int, duration: float = 0.8) -> Dict[str, Any]:
    """
    Sposta il mouse alle coordinate indicate con una traiettoria fluida e visibile.
    Usa SetCursorPos con interpolazione sigmoidale naturale a 60 FPS.
    """
    attach_to_user_desktop()
    start_x, start_y = get_mouse_position()
    
    steps = max(15, int(duration * 60))
    step_delay = duration / steps
    user32 = ctypes.windll.user32 if sys.platform == "win32" else None
    
    for i in range(1, steps + 1):
        t = i / steps
        # Easing cubic easeInOut per movimento umano
        smooth_t = t * t * (3 - 2 * t)
        cur_x = int(start_x + (target_x - start_x) * smooth_t)
        cur_y = int(start_y + (target_y - start_y) * smooth_t)
        
        if user32:
            user32.SetCursorPos(cur_x, cur_y)
        elif pyautogui:
            pyautogui.moveTo(cur_x, cur_y)
        time.sleep(step_delay)
        
    final_x, final_y = get_mouse_position()
    return {
        "success": True,
        "from": (start_x, start_y),
        "to": (final_x, final_y),
        "duration": duration
    }

def click_at(x: int, y: int, button: str = "left", double: bool = False, duration: float = 0.6) -> Dict[str, Any]:
    """
    Muove il mouse fluidamente verso (x, y) ed esegue un click sul desktop.
    """
    attach_to_user_desktop()
    smooth_move(x, y, duration=duration)
    time.sleep(0.08)
    
    if sys.platform == "win32":
        user32 = ctypes.windll.user32
        down_flag = 0x0002 if button == "left" else 0x0008
        up_flag = 0x0004 if button == "left" else 0x0010
        
        user32.mouse_event(down_flag, 0, 0, 0, 0)
        time.sleep(0.05)
        user32.mouse_event(up_flag, 0, 0, 0, 0)
        
        if double:
            time.sleep(0.1)
            user32.mouse_event(down_flag, 0, 0, 0, 0)
            time.sleep(0.05)
            user32.mouse_event(up_flag, 0, 0, 0, 0)
    elif pyautogui:
        if double:
            pyautogui.doubleClick(button=button)
        else:
            pyautogui.click(button=button)
            
    return {
        "success": True,
        "action": "double_click" if double else "click",
        "button": button,
        "at": (x, y)
    }

def type_text(text: str, interval: float = 0.03) -> Dict[str, Any]:
    """Digita testo con cadenza naturale."""
    attach_to_user_desktop()
    if pyautogui:
        pyautogui.write(text, interval=interval)
        return {"success": True, "chars": len(text)}
    return {"success": False, "error": "pyautogui non disponibile"}

def hotkey(*keys: str) -> Dict[str, Any]:
    """Preme combinazioni di tasti (es: 'win', 'r')."""
    attach_to_user_desktop()
    if pyautogui:
        pyautogui.hotkey(*keys)
        return {"success": True, "keys": keys}
    return {"success": False, "error": "pyautogui non disponibile"}

def take_screenshot(save_path: Optional[str] = None):
    """
    Cattura l'intero schermo dal desktop visibile.
    Restituisce un oggetto PIL.Image.
    """
    attach_to_user_desktop()
    img = ImageGrab.grab()
    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        img.save(save_path)
    return img

def demo_glide():
    """
    Dimostrazione del controllo visibile:
    Muove il mouse in un percorso a triangolo al centro dello schermo.
    """
    attach_to_user_desktop()
    w, h = get_screen_size()
    cx, cy = w // 2, h // 2
    
    print(f"Mamba User Moves: schermo {w}x{h}, mouse attuale {get_mouse_position()}")
    print("Inizio movimento triangolare visibile...")
    
    points = [
        (cx, cy - 150),
        (cx + 200, cy + 150),
        (cx - 200, cy + 150),
        (cx, cy)
    ]
    for px, py in points:
        smooth_move(px, py, duration=0.7)
        time.sleep(0.1)
        
    print("Movimento completato. Mouse a:", get_mouse_position())
    return {"success": True, "final_pos": get_mouse_position()}

if __name__ == "__main__":
    demo_glide()
