#!/usr/bin/env python3
"""
mamba/moves/saluto_stefano.py - User Moves: Apertura Blocco Note e Buongiorno al Signor Stefano.
Flusso:
1. Trova o avvia Blocco Note
2. Porta in primo piano e ripristina (Win32 SW_RESTORE)
3. Crea una nuova nota pulita (Ctrl+N)
4. Muove il mouse visibilmente nell'area di scrittura e clicca
5. Digita il messaggio di buongiorno da parte di Dany con augurio e saluto finale in Cinese
"""

import time
import sys
import ctypes
import pyautogui
import pygetwindow as gw
import pyperclip

from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size,
    get_mouse_position,
    smooth_move,
    click_at,
    type_text,
    hotkey
)

def saluta_signor_stefano():
    attach_to_user_desktop()
    print("=== MAMBA OS: USER MOVES -> BUONGIORNO SIGNOR STEFANO ===")

    user32 = ctypes.windll.user32

    # 1. Trova finestra Blocco Note o avviala
    wins = [w for w in gw.getWindowsWithTitle("Blocco note") if w.title]
    if not wins:
        print("[1/5] Apertura Blocco Note da tasto Win...")
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write("notepad", interval=0.05)
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.8)
        wins = [w for w in gw.getWindowsWithTitle("Blocco note") if w.title]

    if not wins:
        print("❌ Impossibile trovare o aprire Blocco Note.")
        return False

    notepad = wins[0]
    hwnd = notepad._hWnd
    print(f"[1/5] Finestra Blocco Note agganciata (HWND: {hwnd})")

    # Ripristina e porta in primo piano al 100%
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    time.sleep(0.3)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.6)

    # 2. Apri nuova scheda/nota con Ctrl+N
    print("[2/5] Apertura nuova nota pulita (Ctrl+N)...")
    pyautogui.hotkey("ctrl", "n")
    time.sleep(0.6)

    # 3. Sposta il mouse nell'area di digitazione
    screen_w, screen_h = get_screen_size()
    # Punto centrale ideale per la scrittura
    target_x = max(200, min(screen_w - 300, 600))
    target_y = max(200, min(screen_h - 300, 400))

    print(f"[3/5] 🖱️ Muovo il mouse nell'area testo a ({target_x}, {target_y}) e clicco...")
    click_at(target_x, target_y, duration=0.8)
    time.sleep(0.4)

    # 4. Componi il messaggio
    messaggio = (
        "Buongiorno Signor Stefano!\n\n"
        "Le auguro una splendida, serena e produttiva giornata da parte di Dany.\n\n"
        "Saluto e augurio speciale in Cinese per Lei:\n"
        "祝您度过美好的一天，事事顺心！\n"
        "(Zhù nín dùguò měihǎo de yī tiān, shìshì shùnxīn!\n"
        "— Che la Sua giornata sia splendida e ogni cosa vada per il meglio!)\n\n"
        "再见！ (Zàijiàn! — A presto e buona continuazione!)\n\n"
        "Con sincera stima e amicizia,\n"
        "Dany & Mamba OS 🐍\n"
    )

    print("[4/5] ⌨️ Inserimento testo con resa perfetta caratteri cinesi...")
    pyperclip.copy(messaggio)
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.0)

    # 5. Sposta il mouse dolcemente da parte
    smooth_move(target_x + 350, target_y + 200, duration=0.7)

    print("\n✅ Perfetto! Messaggio di buongiorno per il Signor Stefano scritto con successo sul Blocco Note!")
    return True

if __name__ == "__main__":
    saluta_signor_stefano()
