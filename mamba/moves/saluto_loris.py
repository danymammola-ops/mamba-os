#!/usr/bin/env python3
"""
mamba/moves/saluto_loris.py - User Moves: Apertura Blocco Note e Saluto Speciale al Signor Loris.
Include:
- Apertura/Focus di Blocco Note
- Nuova nota pulita (Ctrl+N)
- Click nell'area di testo
- Digitazione del saluto gentile a nome di Dany
- Frasi in Cinese (你好 - Nǐ hǎo) e Africano (Swahili: Jambo / Sawubona)
"""

import time
import sys
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

def saluta_signor_loris():
    attach_to_user_desktop()
    print("=== MAMBA OS: USER MOVES -> SALUTO AL SIGNOR LORIS ===")

    # 1. Trova o avvia Blocco Note
    windows = [w for w in gw.getWindowsWithTitle("Blocco note") if w.title]
    if not windows:
        print("[1/4] Apertura Blocco Note tramite tasto Win...")
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write("notepad", interval=0.05)
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.8)
        windows = [w for w in gw.getWindowsWithTitle("Blocco note") if w.title]

    if not windows:
        print("❌ Impossibile trovare la finestra del Blocco Note.")
        return False

    notepad = windows[0]
    print(f"[1/4] Blocco Note trovato a ({notepad.left}, {notepad.top}), dim {notepad.width}x{notepad.height}")

    # Ripristina se minimizzato e porta in primo piano
    if notepad.isMinimized:
        notepad.restore()
        time.sleep(0.5)
    try:
        notepad.activate()
    except Exception:
        pass
    time.sleep(0.6)

    # 2. Crea nuova nota (Ctrl+N)
    print("[2/4] Apertura nuova nota con Ctrl+N...")
    pyautogui.hotkey("ctrl", "n")
    time.sleep(0.6)

    # 3. Sposta il mouse nell'area di testo e clicca
    text_x = notepad.left + min(350, max(150, notepad.width // 2))
    text_y = notepad.top + min(250, max(150, notepad.height // 2))
    print(f"[3/4] 🖱️ Muovo il mouse nell'area di scrittura a ({text_x}, {text_y})...")
    click_at(text_x, text_y, duration=0.8)
    time.sleep(0.4)

    # 4. Componi il testo con saluto gentile, Cinese e Africano
    messaggio = (
        "Gentilissimo Signor Loris,\n\n"
        "Le porgo i miei più cordiali, calorosi e gentili saluti da parte di Dany!\n\n"
        "Un augurio speciale anche in diverse lingue del mondo:\n"
        "• Cinese: 你好 (Nǐ hǎo) — Ti auguro pace, salute e serenità!\n"
        "• Africano (Swahili): Jambo sana! (Un caloroso saluto di prosperità e benvenuto)\n"
        "• Africano (Zulu): Sawubona! (Ti vedo e ti rispetto con stima)\n\n"
        "Con viva stima e simpatia,\n"
        "Dany & Mamba OS 🐍\n"
    )

    print("[4/4] ⌨️ Digitazione fluida del messaggio...")
    # Usiamo pyperclip + Ctrl+V per garantire la perfetta resa dei caratteri cinesi ed emoji
    pyperclip.copy(messaggio)
    time.sleep(0.2)
    pyautogui.hotkey("ctrl", "v")
    time.sleep(1.0)

    # Sposta il mouse dolcemente a riposo fuori dall'area di lettura
    smooth_move(notepad.left + notepad.width - 50, notepad.top + notepad.height - 50, duration=0.6)

    print("\n✅ Messaggio scritto perfettamente sul Blocco Note!")
    return True

if __name__ == "__main__":
    saluta_signor_loris()
