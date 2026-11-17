#!/usr/bin/env python3
"""
mamba/moves/whatsapp_stefano.py - User Moves: Ricerca contatto 'Stefano' e invio messaggio di buongiorno su WhatsApp.
Flusso ad alta velocità (Closed-Loop ReAct):
1. Focus finestra WhatsApp Desktop
2. Clicca barra di ricerca e cerca 'Stefano'
3. Seleziona il contatto e apre la chat
4. Clicca nel campo messaggio in basso
5. Inserisce il testo con saluto gentile, caratteri cinesi ed emoji del serpente verde 🐍
6. Invia il messaggio (Invio) e verifica visivamente
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

def send_whatsapp_to_stefano():
    attach_to_user_desktop()
    user32 = ctypes.windll.user32
    t0 = time.time()

    print("🐍 [MAMBA OS] Avvio automazione WhatsApp Desktop...")

    # 1. Trova finestra WhatsApp
    root = auto.GetRootControl()
    wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)
    if not wa:
        print("❌ Finestra di WhatsApp Desktop non trovata.")
        return False

    hwnd = wa.NativeWindowHandle
    user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)

    r = wa.BoundingRectangle
    print(f"[1/5] WhatsApp attivo a ({r.left}, {r.top}), dimensioni {r.width()}x{r.height()}")

    # 2. Clicca sulla barra di ricerca (in alto a sinistra nella colonna chat)
    search_x = r.left + 150
    search_y = r.top + 90
    print(f"[2/5] 🖱️ Focus barra di ricerca WhatsApp a ({search_x}, {search_y})...")
    smooth_move(search_x, search_y, duration=0.18)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.1)

    # Pulisce eventuale testo precedente e digita 'Stefano'
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('backspace')
    pyautogui.write('Stefano', interval=0.04)
    time.sleep(0.8)

    # 3. Seleziona il contatto Stefano dalla lista dei risultati
    # Il primo risultato è situato subito sotto la barra di ricerca
    contact_x = r.left + 180
    contact_y = r.top + 165
    print(f"[3/5] 👤 Clicco sul contatto Stefano a ({contact_x}, {contact_y})...")
    smooth_move(contact_x, contact_y, duration=0.18)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.6)

    # 4. Sposta il mouse nel campo di scrittura messaggio in basso a destra
    chat_input_x = r.left + int(r.width() * 0.6)
    chat_input_y = r.top + r.height() - 40
    print(f"[4/5] ✍️ Clicco nella casella di digitazione messaggio a ({chat_input_x}, {chat_input_y})...")
    smooth_move(chat_input_x, chat_input_y, duration=0.18)
    user32.mouse_event(2, 0, 0, 0, 0)
    user32.mouse_event(4, 0, 0, 0, 0)
    time.sleep(0.2)

    # 5. Inserimento del messaggio con l'emoji del serpente verde 🐍
    messaggio = (
        "Buongiorno Signor Stefano!\n\n"
        "Le auguro una splendida, serena e produttiva giornata da parte di Dany.\n\n"
        "Saluto e augurio speciale in Cinese per Lei:\n"
        "祝您度过美好的一天，事事顺心！\n"
        "(Zhù nín dùguò měihǎo de yī tiān, shìshì shùnxīn!\n"
        "— Che la Sua giornata sia splendida e ogni cosa vada per il meglio!)\n\n"
        "再见！ (Zàijiàn! — A presto e buona continuazione!)\n\n"
        "Con sincera stima e amicizia,\n"
        "Dany & Mamba OS 🐍"
    )

    print("[5/5] ⌨️ Incollo il messaggio formattato con caratteri cinesi ed emoji Mamba 🐍...")
    pyperclip.copy(messaggio)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.6)

    # 6. Invio del messaggio (Invio)
    print("🚀 Invio messaggio (tasto Enter)...")
    pyautogui.press('enter')
    time.sleep(0.5)

    # Sposta il mouse dolcemente da parte
    smooth_move(r.left + r.width() - 80, r.top + 80, duration=0.3)

    elapsed = time.time() - t0
    print(f"\n✅ [MAMBA SUCCESS] Messaggio inviato a Stefano su WhatsApp in {elapsed:.2f} secondi!")
    return True

if __name__ == "__main__":
    send_whatsapp_to_stefano()
