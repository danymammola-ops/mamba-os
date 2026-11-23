#!/usr/bin/env python3
"""
mamba/console.py - Console di Collegamento & Smart Router Gateway per Mamba OS
Orchestra le richieste decidendo intelligentemente la strada più veloce ed economica:
1. TESTO / CHAT / TRADUZIONI -> FreeLLMAPI locale (0 TOKEN PAGATI, 0€)
2. AUTOMAZIONI DESKTOP (WhatsApp, Meet, Spotify) -> Squadra Micro-Agenti con Safety Gate
3. CODICE / REFACTOR / GIT -> Claude Code CLI
"""

import sys
import os
import json
import time
import subprocess
from typing import Dict, Any, Optional

# Stili ANSI per la grafica Emerald Viper
GREEN = "\033[92m"
EMERALD = "\033[38;2;0;255;136m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.core.freellm_client import FreeLLMClient
from mamba.agents.apps.whatsapp_agent import WhatsAppAgent
from mamba.agents.apps.system_agent import SystemAgent

class MambaConsole:
    def __init__(self):
        self.freellm = FreeLLMClient()
        self.whatsapp = WhatsAppAgent()
        self.system = SystemAgent()
        self.session_tokens_saved = 0

    def print_banner(self):
        """Stampa l'HUD grafico della Console di Collegamento."""
        print(f"\n{EMERALD}{BOLD}")
        print("    ╔══════════════════════════════════════════════════════════════╗")
        print("    ║   🐍  MAMBA OS  —  CONSOLE DI COLLEGAMENTO & ROUTER GATEWAY ║")
        print("    ╚══════════════════════════════════════════════════════════════╝")
        print(f"{RESET}")
        
        # Telemetria connessioni
        freellm_status = f"{GREEN}● ONLINE (300+ Modelli, 0€ Token){RESET}" if self.freellm.api_key else f"{RED}● OFFLINE{RESET}"
        claude_status = f"{GREEN}● DISPONIBILE (CLI Locale){RESET}"
        agents_status = f"{GREEN}● PRONTI (WhatsApp, Snap, Processi){RESET}"

        print(f" {BOLD}STATO COLLEGAMENTI SISTEMA:{RESET}")
        print(f"   ► FreeLLMAPI Gateway:    {freellm_status}")
        print(f"   ► Ingegneria Codice:     {claude_status}")
        print(f"   ► Flotta Micro-Agenti:   {agents_status}")
        print(f"   ► Token Guard Memoria:   {CYAN}0 / 50.000 Token (0%){RESET}")
        print(f"{DIM}────────────────────────────────────────────────────────────────────{RESET}\n")

    def route_request(self, user_prompt: str) -> Dict[str, Any]:
        """
        Analizza la richiesta dell'utente e decide la rotta:
        - 'text': solo testo/chat -> FreeLLMAPI a 0 token
        - 'whatsapp': invio messaggi -> WhatsAppAgent
        - 'window': ridimensionamento/meet -> SystemAgent
        - 'close': chiusura app -> SystemAgent
        - 'claude': refactoring/file/git -> Claude Code
        """
        p = user_prompt.lower().strip()

        # 1. Riconoscimento Automazioni Desktop
        if "whatsapp" in p or "manda a " in p or "scrivi a " in p or "messaggio a" in p:
            return {"type": "whatsapp"}
        
        if "chiudi spotify" in p or "stop spotify" in p:
            return {"type": "close_app", "app": "spotify"}
        
        if "meet" in p and ("50%" in p or "metà" in p or "snap" in p or "affianca" in p):
            return {"type": "snap_window", "window": "meet", "dir": "left"}

        # 2. Riconoscimento compiti di Codice / Ingegneria
        if p.startswith("/code") or p.startswith("refactor") or "crea un file" in p or "fai git push" in p:
            return {"type": "claude"}

        # 3. Default: PURO TESTO / CHAT / TRADUZIONE / CONOSCENZA -> FreeLLMAPI a ZERO TOKEN!
        return {"type": "text"}

    def execute(self, user_prompt: str):
        """Esegue il comando smistando al motore appropriato."""
        route = self.route_request(user_prompt)
        rtype = route["type"]

        # ==========================================
        # ROTTA 1: PURO TESTO (FreeLLMAPI - 0 Token)
        # ==========================================
        if rtype == "text":
            print(f"{CYAN}{BOLD}⚡ [FREELLMAPI ROUTE] Richiesta testuale -> Modello Gratuito (0 Token Pagati, 0€){RESET}")
            t0 = time.time()
            try:
                system_instruction = (
                    "Sei Mamba OS, un sistema operativo cognitivo personale e brillante. "
                    "Rispondi in modo naturale, veloce, diretto ed empatico. Se ti chiedono traduzioni in cinese o saluti, "
                    "fornisci sempre i caratteri, il pinyin e il significato."
                )
                messages = [
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": user_prompt}
                ]
                res = self.freellm.chat(messages, model="auto:fast", temperature=0.7)
                elapsed = time.time() - t0
                
                print(f"{EMERALD}{BOLD}\n🐍 Mamba:{RESET}\n{res['content'].strip()}\n")
                print(f"{DIM}⏱️ Risposto in {elapsed:.2f}s tramite {res.get('provider', 'FreeLLMAPI')} | Costo: 0.00€{RESET}\n")
                return res['content']
            except Exception as e:
                print(f"{RED}❌ Errore FreeLLMAPI: {e}{RESET}")
                return None

        # ==========================================
        # ROTTA 2: WHATSAPP AGENT (Micro-Agente)
        # ==========================================
        elif rtype == "whatsapp":
            print(f"{GREEN}{BOLD}📱 [MICRO-AGENTE WHATSAPP] Automazione Desktop a circuito chiuso con Safety Gate...{RESET}")
            
            # Chiediamo prima a FreeLLMAPI (a 0 token) di formattare il messaggio se c'è una richiesta creativa
            recipient = "Gabriele Vinted" if "gabriele" in user_prompt.lower() else "Stefano"
            
            # Genera il messaggio tramite FreeLLMAPI
            print(f" -> Generazione testo messaggio tramite FreeLLMAPI...")
            gen_prompt = f"Scrivi un messaggio breve e simpatico per {recipient}: {user_prompt}"
            msg_res = self.freellm.chat([{"role": "user", "content": gen_prompt}], model="auto:fast")
            final_message = msg_res['content'].strip()
            
            print(f" -> Messaggio preparato per {recipient}.")
            # Esegui con l'agente
            return self.whatsapp.send_message(recipient, final_message)

        # ==========================================
        # ROTTA 3: SISTEMA / FINESTRE (System Agent)
        # ==========================================
        elif rtype == "close_app":
            print(f"{YELLOW}{BOLD}🪟 [SYSTEM AGENT] Chiusura applicazione {route['app']}...{RESET}")
            return self.system.close_app(route["app"])

        elif rtype == "snap_window":
            print(f"{YELLOW}{BOLD}🪟 [SYSTEM AGENT] Posizionamento finestra {route['window']} al 50%...{RESET}")
            return self.system.snap_window(route["window"], direction=route["dir"])

        # ==========================================
        # ROTTA 4: CLAUDE CODE (Ingegnere Codice)
        # ==========================================
        elif rtype == "claude":
            print(f"{CYAN}{BOLD}🛠️ [CLAUDE CODE CLI] Passaggio del compito all'agente di programmazione...{RESET}")
            subprocess.run(["claude", user_prompt], shell=True)

    def interactive_loop(self):
        """Avvia la console interattiva in tempo reale."""
        self.print_banner()
        print(f"{BOLD}Inserisci un comando o una domanda (digita 'exit' per uscire):{RESET}")
        
        while True:
            try:
                prompt = input(f"{EMERALD}mamba>{RESET} ").strip()
                if not prompt:
                    continue
                if prompt.lower() in ["exit", "quit", "esci"]:
                    print(f"{EMERALD}A presto! Mamba OS in standby.{RESET}")
                    break
                self.execute(prompt)
            except KeyboardInterrupt:
                print(f"\n{EMERALD}Uscita dalla Console di Collegamento.{RESET}")
                break

if __name__ == "__main__":
    console = MambaConsole()
    if len(sys.argv) > 1:
        # Modalità a singolo comando da CLI (es. python mamba/console.py "spiegami la relatività")
        full_prompt = " ".join(sys.argv[1:])
        console.print_banner()
        console.execute(full_prompt)
    else:
        # Modalità interattiva REPL
        console.interactive_loop()
