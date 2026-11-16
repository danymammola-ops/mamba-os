#!/usr/bin/env python3
"""
mamba/moves/demo_notepad_flow.py - Dimostrazione completa Computer Use:
1. Apre Blocco Note
2. Apre una nuova nota
3. Muove il mouse e scrive 'ciao a tutti'
4. Usa l'agente visivo per trovare il pulsante Riduci a icona ('-') in alto a destra
5. Fa scivolare il mouse e ci clicca sopra, togliendo la pagina senza chiuderla!
"""

import subprocess
import time
import sys
import ctypes

from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size,
    get_mouse_position,
    smooth_move,
    click_at,
    type_text,
    hotkey
)
from mamba.moves.visual_agent import VisualAgent

def run_flow():
    attach_to_user_desktop()
    print("=== MAMBA OS: APERTURA E GESTIONE BLOCCO NOTE ===")
    
    # 1. Avvia Blocco Note
    print("[1/5] Avvio di notepad.exe...")
    subprocess.Popen(["notepad.exe"])
    time.sleep(1.2)
    attach_to_user_desktop()

    # 2. Crea una nuova nota (Ctrl+N per essere sicuri)
    print("[2/5] Apertura nuova nota...")
    hotkey("ctrl", "n")
    time.sleep(0.5)

    # 3. Sposta il mouse nell'area di testo e clicca
    screen_w, screen_h = get_screen_size()
    text_area_x = screen_w // 2
    text_area_y = screen_h // 2
    print(f"[3/5] Muovo il cursore al centro dell'area di scrittura ({text_area_x}, {text_area_y})...")
    click_at(text_area_x, text_area_y, duration=0.8)
    time.sleep(0.4)

    # Scrivi 'ciao a tutti'
    print("[3/5] Digitazione del testo: 'ciao a tutti'...")
    type_text("ciao a tutti", interval=0.08)
    time.sleep(1.2)

    # 4. Usa il Visual Agent per cercare il pulsante '-' (Riduci a icona) in alto a destra
    print("[4/5] 📸 Visual Agent: Ricerca visiva del pulsante Riduci a icona ('-')...")
    agent = VisualAgent(model="gemini-flash-lite")
    
    target_desc = "il pulsante Riduci a icona (il trattino meno '-') in alto a destra della finestra del Blocco Note"
    target = agent.locate_element(target_desc)
    
    if target.get("found") and target["x"] > 0:
        tx, ty = target["x"], target["y"]
        print(f"[5/5] 🎯 Trovato pulsante '-' a ({tx}, {ty}) in {target['latency']}s!")
        print(f"[5/5] 🖱️ Muovo il mouse verso il pulsante '-' e clicco per minimizzare...")
        click_at(tx, ty, duration=0.9)
    else:
        print("[5/5] Visual fallback: calcolo coordinate standard finestra in alto a destra...")
        # In Windows 11 a tutto schermo o finestra tipica, il pulsante minimizza è a circa w - 140px, h: 15-20px
        # Se la finestra è centrata (es. 1000x700), clicchiamo nell'area top-right
        click_at(screen_w - 140, 18, duration=0.9)

    print("\n✅ Sequenza completata: Blocco Note aperto, testo scritto e finestra minimizzata senza chiuderla!")

if __name__ == "__main__":
    run_flow()
