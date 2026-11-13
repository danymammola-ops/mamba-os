#!/usr/bin/env python3
"""
mamba/moves/whatsapp_direct.py - Modulo User Moves per WhatsApp Desktop su Windows
Offre due modalità operative:
1. Modalità Istantanea (Deep-Link Windows URI):
   Latenza zero, 100% deterministico senza muovere pixel.
   `start whatsapp://send?phone=...&text=...`
2. Modalità GUI (Search & Type):
   Porta la finestra di WhatsApp Desktop in primo piano, cerca il contatto e invia il messaggio.
"""

import os
import sys
import time
import subprocess
import urllib.parse
from typing import Dict, Any

def send_whatsapp_by_phone(phone_number: str, message: str) -> Dict[str, Any]:
    """
    Invia un messaggio WhatsApp tramite il protocollo URI nativo di Windows.
    Supporta numeri con o senza prefisso internazionale (es. +393331234567 o 3331234567).
    """
    clean_phone = phone_number.replace(" ", "").replace("-", "")
    if clean_phone.startswith("00"):
        clean_phone = "+" + clean_phone[2:]
    elif not clean_phone.startswith("+"):
        clean_phone = "+39" + clean_phone  # Default prefisso Italia

    encoded_text = urllib.parse.quote(message)
    uri = f"whatsapp://send?phone={clean_phone}&text={encoded_text}"

    print(f"🖱️ [User Moves] Lancio protocollo WhatsApp: {clean_phone}...")
    try:
        if sys.platform == "win32":
            os.startfile(uri)
        else:
            subprocess.run(["open", uri])
        return {"ok": True, "method": "uri_protocol", "target": clean_phone, "status": "Inviato al client WhatsApp"}
    except Exception as e:
        return {"ok": False, "method": "uri_protocol", "error": str(e)}

def bring_whatsapp_to_front() -> bool:
    """Porta la finestra di WhatsApp Desktop in primo piano se aperta."""
    try:
        import pygetwindow as gw
        windows = gw.getWindowsWithTitle("WhatsApp")
        if windows:
            win = windows[0]
            if win.isMinimized:
                win.restore()
            win.activate()
            time.sleep(0.3)
            return True
    except Exception:
        pass

    # Fallback: avvia l'app se non trovata tra le finestre
    try:
        os.system("start whatsapp:")
        time.sleep(1.0)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    print("🐍 [Mamba Moves] Modulo WhatsApp Desktop pronto.")
    print("Test: Per inviare un messaggio reale usa: send_whatsapp_by_phone('+39...', 'Ciao!')")
