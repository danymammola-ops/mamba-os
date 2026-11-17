#!/usr/bin/env python3
"""
mamba/moves/send_mamma.py - User Moves: Invio messaggio spontaneo e affettuoso alla Mamma su WhatsApp.
"""

import time
import sys
import ctypes
import pyautogui
import pyperclip

from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size,
    smooth_move,
    click_at,
    take_screenshot
)
attach_to_user_desktop()
import uiautomation as auto

def send_to_mamma():
    attach_to_user_desktop()
    user32 = ctypes.windll.user32
    t0 = time.time()

    print("❤️ [MAMBA OS] Avvio invio messaggio affettuoso alla Mamma...")

    # 1. Trova finestra WhatsApp
    root = auto.GetRootControl()
    wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)
    if not wa:
        print("❌ Finestra di WhatsApp non trovata.")
        return False

    hwnd = wa.NativeWindowHandle
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)

    r = wa.BoundingRectangle
    print(f"[1/4] WhatsApp attivo a ({r.left}, {r.top}), dim {r.width()}x{r.height()}")

    # 2. Clicca sul contatto 'Mamma' identificato dalla visione a (363, 746) o nella lista
    contact_x = 363
    contact_y = 746
    print(f"[2/4] 🖱️ Clicco sul contatto Mamma a ({contact_x}, {contact_y})...")
    smooth_move(contact_x, contact_y, duration=0.18)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.5)

    # 3. Clicca nella casella di digitazione del messaggio
    input_x = 587
    input_y = 856
    # Assicuriamoci che le coordinate siano all'interno della finestra
    if input_y > r.bottom - 10:
        input_y = r.bottom - 40
    print(f"[3/4] ✍️ Focus casella di scrittura a ({input_x}, {input_y})...")
    smooth_move(input_x, input_y, duration=0.15)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.2)

    # 4. Messaggio spontaneo e naturale in prima persona da parte di Dany
    messaggio = (
        "Ciao mamma! ❤️ Volevo solo scriverti al volo per ricordarti quanto ti voglio bene "
        "e che sei sempre nei miei pensieri. Spero che stia andando bene la giornata! "
        "Ci sentiamo dopo con calma, un bacione grandissimo 🥰"
    )

    print("[4/4] ⌨️ Inserimento del messaggio affettuoso...")
    pyperclip.copy(messaggio)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.6)

    # Invio
    print("🚀 Invio del messaggio (Enter)...")
    pyautogui.press('enter')
    time.sleep(0.5)

    # Sposta il mouse dolcemente da parte
    smooth_move(r.left + r.width() - 60, r.top + 60, duration=0.3)

    elapsed = time.time() - t0
    print(f"\n✅ [MAMBA SUCCESS] Messaggio inviato alla Mamma in {elapsed:.2f} secondi!")
    return True

if __name__ == "__main__":
    send_to_mamma()
