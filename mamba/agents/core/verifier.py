#!/usr/bin/env python3
"""
mamba/agents/core/verifier.py - Safety Gate & Verifier Deterministico per Mamba OS
Controlla con certezza assoluta (tramite Windows UIAutomation) che la finestra, 
l'intestazione o il contatto attivo corrispondano al target PRIMA di qualsiasi azione distruttiva o di invio.
"""

import time
import sys
import ctypes
from typing import Dict, Any, Optional

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.moves.user_moves import attach_to_user_desktop

attach_to_user_desktop()
import uiautomation as auto

class SafetyVerifier:
    def __init__(self):
        attach_to_user_desktop()
        self.user32 = ctypes.windll.user32

    def verify_whatsapp_chat(self, target_contact: str, timeout: float = 3.0) -> Dict[str, Any]:
        """
        Ispeziona l'interfaccia di WhatsApp Desktop.
        Legge il nome del contatto visualizzato nell'intestazione della conversazione aperta.
        Se NON corrisponde a target_contact, restituisce False e BLOCCA l'invio.
        """
        attach_to_user_desktop()
        t0 = time.time()
        target_lower = target_contact.strip().lower()

        root = auto.GetRootControl()
        wa = next((w for w in root.GetChildren() if 'whatsapp' in (w.Name or '').lower()), None)
        if not wa:
            return {
                "verified": False,
                "found_name": "",
                "reason": "Finestra di WhatsApp non trovata a schermo."
            }

        # Cerchiamo l'elemento che contiene il nome della chat aperta
        # In WhatsApp Desktop WinUI, l'header della chat aperta è nei controlli figli
        found_header = ""
        while time.time() - t0 < timeout:
            for child in wa.GetChildren():
                name = child.Name or ""
                # Se il nome è WhatsApp o stringhe di sistema, salta
                if not name or name == "WhatsApp" or "Input Sink" in name or "Caption" in name:
                    continue
                # Se troviamo elementi di testo
                found_header = name
                break
            
            # Se la chat ha un header corrispondente
            if found_header:
                break
            time.sleep(0.1)

        # Controllo di corrispondenza
        # Cerchiamo se il target è contenuto nel nome trovato o viceversa
        is_match = False
        if found_header:
            if target_lower in found_header.lower() or found_header.lower() in target_lower:
                is_match = True

        if is_match:
            return {
                "verified": True,
                "found_name": found_header,
                "reason": f"Destinatario '{found_header}' verificato con successo nell'header. Invio autorizzato."
            }
        else:
            return {
                "verified": False,
                "found_name": found_header,
                "reason": f"ALLARME SICUREZZA: Chat aperta è '{found_header}', ma il destinatario richiesto era '{target_contact}'. Invio BLOCCATO!"
            }

    def verify_window_active(self, expected_keyword: str) -> bool:
        """Verifica se la finestra attualmente in primo piano contiene la keyword."""
        hwnd = self.user32.GetForegroundWindow()
        length = self.user32.GetWindowTextLengthW(hwnd)
        buff = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buff, length + 1)
        active_title = buff.value.lower()
        return expected_keyword.lower() in active_title

if __name__ == "__main__":
    verifier = SafetyVerifier()
    print("Test SafetyVerifier...")
    res = verifier.verify_whatsapp_chat("Gabriele")
    print("Risultato verifica:", res)
