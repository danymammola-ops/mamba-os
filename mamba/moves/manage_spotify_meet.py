#!/usr/bin/env python3
"""
mamba/moves/manage_spotify_meet.py - Gestione finestre:
1. Chiude Spotify
2. Ridimensiona e posiziona la finestra di Google Meet al 50% dello schermo (NON chiuderla!)
"""

import sys
import os
import time
import ctypes
import pyautogui

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size
)

# 1. Aggancio al desktop dell'utente PRIMA di importare uiautomation
attach_to_user_desktop()
import uiautomation as auto

def manage_windows():
    attach_to_user_desktop()
    user32 = ctypes.windll.user32
    screen_w, screen_h = get_screen_size()
    print(f"🖥️ Risoluzione schermo: {screen_w}x{screen_h}")

    root = auto.GetRootControl()
    children = root.GetChildren()

    print(f"Trovate {len(children)} finestre di primo livello:")
    spotify_window = None
    meet_window = None

    for child in children:
        name = child.Name or ""
        cls = child.ClassName or ""
        hwnd = child.NativeWindowHandle
        name_lower = name.lower()

        if "spotify" in name_lower or "spotify" in cls.lower():
            print(f" -> [SPOTIFY] HWND: {hwnd} | Name: '{name}' | Class: '{cls}'")
            spotify_window = child
        elif "meet" in name_lower or "zen" in name_lower or "google meet" in name_lower:
            print(f" -> [MEET CANDIDATE] HWND: {hwnd} | Name: '{name}' | Class: '{cls}'")
            if "meet" in name_lower:
                meet_window = child
            elif not meet_window and "zen" in name_lower:
                meet_window = child

    # --- PASSO 1: CHIUDI SPOTIFY ---
    print("\n--- PASSO 1: Chiusura Spotify ---")
    if spotify_window:
        hwnd_sp = spotify_window.NativeWindowHandle
        print(f"Invio WM_CLOSE a Spotify (HWND {hwnd_sp})...")
        user32.PostMessageW(hwnd_sp, 0x0010, 0, 0) # WM_CLOSE
        time.sleep(1.0)
    
    # Verifica processi Spotify rimasti
    import subprocess
    res = subprocess.run(["powershell", "-Command", "Get-Process spotify -ErrorAction SilentlyContinue"], capture_output=True, text=True)
    if "Spotify" in res.stdout:
        print("Arresto forzato dei processi residui di Spotify...")
        subprocess.run(["powershell", "-Command", "Stop-Process -Name Spotify -Force -ErrorAction SilentlyContinue"], capture_output=True)
        print("Spotify chiuso con successo.")
    else:
        print("Nessun processo Spotify attivo.")

    # --- PASSO 2: METTI MEET AL 50% (NON CHIUDERE!) ---
    print("\n--- PASSO 2: Posizionamento Google Meet al 50% ---")
    if not meet_window:
        # Ricontrolla figli
        children = root.GetChildren()
        for child in children:
            name = (child.Name or "").lower()
            if "meet" in name or "zen" in name:
                meet_window = child
                break

    if not meet_window:
        print("❌ Finestra di Google Meet / Browser non trovata!")
        return False

    hwnd_meet = meet_window.NativeWindowHandle
    print(f"Finestra Meet identificata: '{meet_window.Name}' (HWND {hwnd_meet})")

    # Ripristina e porta in primo piano
    user32.ShowWindow(hwnd_meet, 9) # SW_RESTORE
    time.sleep(0.2)
    user32.SetForegroundWindow(hwnd_meet)
    time.sleep(0.4)

    # Usa Win + Left per lo snap nativo al 50% a sinistra
    print("Eseguo snapping Windows al 50% (Win + Left)...")
    pyautogui.hotkey('win', 'left')
    time.sleep(0.5)
    # Esc per togliere eventuale menu snap assist di Windows 11
    pyautogui.press('esc')
    time.sleep(0.4)

    # Verifica dimensioni finali
    rect = meet_window.BoundingRectangle
    w = rect.width()
    h = rect.height()
    print(f"Dimensioni finestra Meet dopo snap: {w}x{h} a ({rect.left}, {rect.top})")

    # Se lo snap non ha funzionato o la larghezza non è vicina al 50%, usiamo SetWindowPos
    target_w = screen_w // 2
    if abs(w - target_w) > 50:
        print(f"Perfeziono dimensioni con MoveWindow: 0, 0, {target_w}, {screen_h - 48}...")
        # SWP_NOZORDER = 0x0004, SWP_SHOWWINDOW = 0x0040
        user32.MoveWindow(hwnd_meet, 0, 0, target_w, screen_h - 48, True)
        time.sleep(0.3)
        rect = meet_window.BoundingRectangle
        print(f"Dimensioni finali Meet: {rect.width()}x{rect.height()} a ({rect.left}, {rect.top})")

    print("\n✅ Completato: Spotify chiuso e Google Meet posizionato al 50% senza chiuderlo!")
    return True

if __name__ == "__main__":
    manage_windows()
