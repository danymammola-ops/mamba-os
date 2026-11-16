#!/usr/bin/env python3
"""
mamba/moves/notepad_user_flow.py - Flusso completo richiesto dall'utente:
1. Apre Blocco Note (se non già aperto)
2. Crea una nuova nota (Ctrl+N)
3. Sposta il mouse nell'area di testo, clicca e digita 'ciao a tutti'
4. Fa scivolare visibilmente il mouse sul tasto meno '-' (Riduci a icona) in alto a destra
5. Clicca il meno per togliere la pagina senza chiuderla (minimizza sulla barra delle applicazioni)
"""

import time
import sys
import pyautogui
import pygetwindow as gw

from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size,
    get_mouse_position,
    smooth_move,
    click_at,
    type_text,
    hotkey
)

def execute_notepad_flow():
    attach_to_user_desktop()
    print("=== MAMBA OS: USER MOVES NOTEPAD ===")
    
    # 1. Trova o apri Blocco Note
    windows = [w for w in gw.getWindowsWithTitle("Blocco note") if w.title]
    if not windows:
        print("[1/5] Blocco Note non aperto. Apertura tramite Start...")
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.write("notepad", interval=0.06)
        time.sleep(0.3)
        pyautogui.press("enter")
        time.sleep(1.8)
        windows = [w for w in gw.getWindowsWithTitle("Blocco note") if w.title]
    
    if not windows:
        print("❌ Impossibile trovare la finestra del Blocco Note.")
        return False
        
    notepad = windows[0]
    print(f"[1/5] Finestra Blocco Note attiva a ({notepad.left}, {notepad.top}), dimensioni {notepad.width}x{notepad.height}")
    
    # Porta in primo piano e ripristina se minimizzata
    if notepad.isMinimized:
        notepad.restore()
        time.sleep(0.5)
    notepad.activate()
    time.sleep(0.5)

    # 2. Apri nuova nota (Ctrl+N)
    print("[2/5] Apertura nuova nota con Ctrl+N...")
    pyautogui.hotkey("ctrl", "n")
    time.sleep(0.6)

    # 3. Sposta il mouse nell'area di digitazione e clicca
    text_x = notepad.left + min(350, notepad.width // 2)
    text_y = notepad.top + min(300, notepad.height // 2)
    print(f"[3/5] 🖱️ Muovo il mouse nell'area testo a ({text_x}, {text_y}) e clicco...")
    click_at(text_x, text_y, duration=0.8)
    time.sleep(0.3)

    # Digita 'ciao a tutti'
    print("[3/5] ⌨️ Digitazione visibile: 'ciao a tutti'...")
    type_text("ciao a tutti\n", interval=0.08)
    time.sleep(1.5)

    # 4. Sposta il mouse sul tasto '-' (Riduci a icona) in alto a destra
    # In Windows 11, il tasto '-' è situato a circa width - 120 dal bordo sinistro, altezza top + 18
    min_btn_x = notepad.left + notepad.width - 118
    min_btn_y = notepad.top + 18
    
    print(f"[4/5] 🎯 Bersaglio: pulsante Riduci a icona '-' a ({min_btn_x}, {min_btn_y})")
    print(f"[4/5] 🖱️ Faccio scivolare il cursore verso il tasto meno '-' in alto a destra...")
    smooth_move(min_btn_x, min_btn_y, duration=1.0)
    time.sleep(0.5)

    # 5. Clicca il meno per togliere la pagina senza chiuderla
    print("[5/5] 👆 Click sul tasto meno '-'! Riduco a icona senza chiudere...")
    click_at(min_btn_x, min_btn_y, duration=0.2)
    time.sleep(0.5)

    print("\n✅ Perfetto! Blocco note aperto, nuova nota creata, 'ciao a tutti' scritto e finestra minimizzata!")
    return True

if __name__ == "__main__":
    execute_notepad_flow()
