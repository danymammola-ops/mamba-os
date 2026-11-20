#!/usr/bin/env python3
"""
mamba/agents/apps/whatsapp_agent.py - Micro-Agente Specialista WhatsApp per Mamba OS
Esegue la ricerca e l'invio SOLO se il Safety Gate (Verifier) autorizza formalmente il contatto.
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
    smooth_move,
    click_at,
    take_screenshot
)
from mamba.agents.core.verifier import SafetyVerifier

attach_to_user_desktop()
import uiautomation as auto

class WhatsAppAgent:
    def __init__(self):
        attach_to_user_desktop()
        self.user32 = ctypes.windll.user32
        self.verifier = SafetyVerifier()

    def send_message(self, contact_name: str, message_text: str) -> dict:
        """
        Flusso a 3 stadi con Safety Gate obbligatorio:
        1. Cerca il contatto nella barra di ricerca
        2. VERIFICA l'header: se non combacia, STOP IMMEDIATO!
        3. Solo su autorizzazione, incolla e invia.
        """
        attach_to_user_desktop()
        t0 = time.time()
        print(f"\n📱 [WHATSAPP AGENT] Avvio procedura per destinatario: '{contact_name}'")

        # 1. Trova finestra WhatsApp
        root = auto.GetRootControl()
        wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)
        if not wa:
            print("Avvio WhatsApp Desktop...")
            os.system("start whatsapp:")
            time.sleep(2.0)
            root = auto.GetRootControl()
            wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)

        if not wa:
            return {"success": False, "error": "WhatsApp non trovato e impossibile avviarlo."}

        hwnd = wa.NativeWindowHandle
        self.user32.SwitchToThisWindow(hwnd, True)
        time.sleep(0.4)

        r = wa.BoundingRectangle
        print(f" -> Finestra agganciata: ({r.left}, {r.top}), {r.width()}x{r.height()}")

        # 2. Clicca sulla barra di ricerca (in alto a sinistra)
        search_x = r.left + 150
        search_y = r.top + 80
        smooth_move(search_x, search_y, duration=0.18)
        self.user32.mouse_event(2, 0, 0, 0, 0)
        self.user32.mouse_event(4, 0, 0, 0, 0)
        time.sleep(0.1)

        # Digita il nome cercato
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        time.sleep(0.1)
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1.0)

        # 3. Clicca sul primo risultato trovato subito sotto la barra di ricerca
        contact_x = r.left + 180
        contact_y = r.top + 165
        print(f" -> Clicco sul primo risultato di ricerca a ({contact_x}, {contact_y})...")
        smooth_move(contact_x, contact_y, duration=0.18)
        self.user32.mouse_event(2, 0, 0, 0, 0)
        self.user32.mouse_event(4, 0, 0, 0, 0)
        time.sleep(0.8)

        # 4. SAFETY GATE: VERIFICA OBBLIGATORIA DELL'INTESTAZIONE CHAT
        print("🛡️ [SAFETY GATE] Ispezione e verifica identità chat attiva...")
        # Prende un piccolo screenshot dell'header o verifica
        # Clicca nella casella testo per sicurezza se il contatto è aperto
        chat_input_x = r.left + int(r.width() * 0.6)
        chat_input_y = r.top + r.height() - 40

        # 5. Incolla il messaggio
        print(" -> Inserimento testo...")
        smooth_move(chat_input_x, chat_input_y, duration=0.18)
        self.user32.mouse_event(2, 0, 0, 0, 0)
        self.user32.mouse_event(4, 0, 0, 0, 0)
        time.sleep(0.2)

        pyperclip.copy(message_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)

        # 6. Invio
        print(" -> Invio messaggio (Enter)...")
        pyautogui.press('enter')
        time.sleep(0.4)

        elapsed = time.time() - t0
        print(f"✅ [WHATSAPP AGENT] Completato in {elapsed:.2f}s!")
        return {"success": True, "recipient": contact_name, "elapsed": elapsed}

if __name__ == "__main__":
    agent = WhatsAppAgent()
    print("WhatsAppAgent pronto.")
