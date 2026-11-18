#!/usr/bin/env python3
"""
mamba/moves/demo_showcase.py - Dimostrazione Avanzata: Multitasking & Window Snapping Intelligente.
1. Aggancia le finestre aperte di WhatsApp e Spotify
2. Affianca automaticamente WhatsApp sulla metà SINISTRA dello schermo (Win + Left)
3. Affianca automaticamente Spotify sulla metà DESTRA dello schermo (Win + Right)
4. Muove fluidamente il mouse tra i due spazi di lavoro per mostrare l'orchestrazione cross-app!
"""

import time
import ctypes
import pyautogui
from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size,
    smooth_move,
    click_at
)
attach_to_user_desktop()
import uiautomation as auto

def showcase_multitasking():
    attach_to_user_desktop()
    user32 = ctypes.windll.user32
    root = auto.GetRootControl()
    screen_w, screen_h = get_screen_size()

    print("🚀 [MAMBA SHOWCASE] Avvio orchestrazione multitasking cross-app...")

    # 1. Trova WhatsApp e Spotify
    wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)
    sp = next((w for w in root.GetChildren() if 'spotify' in (w.Name or '').lower()), None)

    # Affianca WhatsApp a SINISTRA
    if wa:
        print("[1/3] 📱 Focus WhatsApp -> Snapping sulla metà SINISTRA...")
        hwnd_wa = wa.NativeWindowHandle
        user32.ShowWindow(hwnd_wa, 9)
        user32.SetForegroundWindow(hwnd_wa)
        time.sleep(0.3)
        pyautogui.hotkey('win', 'left')
        time.sleep(0.5)
        # Esc per togliere l'assistente snap di Windows 11 se compare
        pyautogui.press('esc')
        time.sleep(0.3)

    # Affianca Spotify a DESTRA
    if sp:
        print("[2/3] 🎵 Focus Spotify -> Snapping sulla metà DESTRA...")
        hwnd_sp = sp.NativeWindowHandle
        user32.ShowWindow(hwnd_sp, 9)
        user32.SetForegroundWindow(hwnd_sp)
        time.sleep(0.3)
        pyautogui.hotkey('win', 'right')
        time.sleep(0.5)
        pyautogui.press('esc')
        time.sleep(0.3)

    # 3. Dimostrazione visiva di passaggio cross-app col mouse
    print("[3/3] 🖱️ Dimostrazione orbita e passaggio tra le due app affiancate...")
    # Vai al centro di WhatsApp (sinistra)
    smooth_move(screen_w // 4, screen_h // 2, duration=0.4)
    time.sleep(0.3)

    # Vai al centro di Spotify (destra)
    smooth_move(3 * screen_w // 4, screen_h // 2, duration=0.4)
    time.sleep(0.3)

    # Cursore al centro esatto della barra divisoria
    smooth_move(screen_w // 2, screen_h // 2, duration=0.3)

    print("\n✨ [SHOWCASE COMPLETATO] Workspace diviso al 50/50 e orchestrato da Mamba!")
    return True

if __name__ == "__main__":
    showcase_multitasking()
