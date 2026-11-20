#!/usr/bin/env python3
"""
mamba/moves/whatsapp_gabriele.py - Invio messaggio a Gabriele su WhatsApp:
- Saluto da parte di Dany
- Augurio per una sessione di gioco di GTA 6 in cinese (con trascrizione e traduzione)
- Esecuzione fluida e verifica visiva
"""

import time
import sys
import os
import ctypes
import pyautogui
import pyperclip

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.moves.user_moves import (
    attach_to_user_desktop,
    get_screen_size,
    smooth_move,
    click_at,
    take_screenshot
)

# Aggancio desktop prima di uiautomation
attach_to_user_desktop()
import uiautomation as auto

def send_whatsapp_to_gabriele():
    attach_to_user_desktop()
    user32 = ctypes.windll.user32
    t0 = time.time()

    print("🚀 [MAMBA OS] Avvio automazione WhatsApp per Gabriele...")

    # 1. Trova o avvia WhatsApp
    root = auto.GetRootControl()
    wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)
    
    if not wa:
        print("Apertura WhatsApp...")
        os.system("start whatsapp:")
        time.sleep(2.0)
        root = auto.GetRootControl()
        wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)

    if not wa:
        print("❌ Finestra di WhatsApp non trovata.")
        return False

    hwnd = wa.NativeWindowHandle
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    time.sleep(0.2)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)

    r = wa.BoundingRectangle
    print(f"[1/5] WhatsApp attivo: ({r.left}, {r.top}), dim {r.width()}x{r.height()}")

    # 2. Clicca barra di ricerca
    search_x = r.left + 150
    search_y = r.top + 90
    print(f"[2/5] 🔍 Focus barra di ricerca a ({search_x}, {search_y})...")
    smooth_move(search_x, search_y, duration=0.18)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.1)

    # Pulisce e cerca 'gabriele vinted'
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    time.sleep(0.1)
    pyperclip.copy("gabriele vinted")
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1.2)

    # 3. Seleziona il contatto Gabriele Vinted
    contact_x = r.left + 180
    contact_y = r.top + 165
    print(f"[3/5] 👤 Clicco sul contatto trovato a ({contact_x}, {contact_y})...")
    smooth_move(contact_x, contact_y, duration=0.18)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.8)

    # 4. Focus campo scrittura messaggio
    chat_input_x = r.left + int(r.width() * 0.6)
    chat_input_y = r.top + r.height() - 40
    print(f"[4/5] ✍️ Clicco nella casella di testo a ({chat_input_x}, {chat_input_y})...")
    smooth_move(chat_input_x, chat_input_y, duration=0.18)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.2)

    # 5. Composizione messaggio
    messaggio = (
        "Ciao Gabriele! Un grande saluto da parte di Dany! 🎮\n\n"
        "Ti auguro una grandissima sessione di gioco su GTA 6! 🚗💥\n\n"
        "祝你《侠盗猎车手6》(GTA 6) 游戏愉快，玩得开心！\n"
        "(Zhù nǐ 《Xiádào Lièchēshǒu 6》 yóuxì yúkuài, wán de kāixīn!\n"
        "— Buona sessione e buon divertimento con GTA 6!)\n\n"
        "Un abbraccio da Dany! 👊🔥"
    )

    print("[5/5] ⌨️ Incollo il messaggio formattato con caratteri cinesi ed emoji...")
    pyperclip.copy(messaggio)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.6)

    # Invio
    print("🚀 Invio messaggio...")
    pyautogui.press('enter')
    time.sleep(0.5)

    # Sposta il mouse dolcemente da parte
    smooth_move(r.left + r.width() - 80, r.top + 80, duration=0.25)

    # Cattura screenshot per verifica visiva
    screenshot_path = r"C:\Users\danym\mio\mamba\mamba\data\verify_gabriele.png"
    os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
    img = take_screenshot()
    img.save(screenshot_path)
    print(f"📸 Screenshot di verifica salvato in: {screenshot_path}")

    elapsed = time.time() - t0
    print(f"\n✨ [SUCCESSO] Messaggio a Gabriele inviato con successo in {elapsed:.2f}s!")
    return True

if __name__ == "__main__":
    send_whatsapp_to_gabriele()
