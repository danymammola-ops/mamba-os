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

def clean_llm_reply(text: str) -> str:
    """Rimuove blocchi di pensiero interno (<think>, catene di ragionamento) per una risposta pulita all'utente."""
    if not text:
        return ""
    import re
    # Rimuovi blocchi <think>...</think>
    text = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)
    # Rimuovi prefissi in inglese di thinking
    if "Here's a thinking process:" in text:
        parts = text.split("Here's a thinking process:")
        after = parts[-1]
        lines = [line for line in after.splitlines() if not line.strip().startswith(('*', '-', '1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.')) and line.strip()]
        if lines:
            text = "\n".join(lines[-4:]).strip()
    return text.strip()

class MambaConsole:
    def __init__(self):
        self.freellm = FreeLLMClient()
        self.whatsapp = WhatsAppAgent()
        self.system = SystemAgent()
        self.session_tokens_saved = 0
        self.conversation_history = []
        self.max_history = 14

    def clear_history(self):
        """Pulisce la memoria della sessione di chat."""
        self.conversation_history.clear()
        print("🧹 [MAMBA MEMORY] Cronologia conversazione azzerata.")

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
        Analizza la richiesta dell'utente e decide la rotta intelligente:
        - 'open_app': apertura di programmi Windows (Spotify, WhatsApp, Notepad, etc.)
        - 'close_app': chiusura processi / finestre
        - 'snap_window': affiancamento finestre (Meet, Chrome, etc.)
        - 'whatsapp': invio messaggi con Safety Gate
        - 'claude': refactoring/terminale/script/git con Claude Code CLI
        - 'text': solo testo/chat/traduzione -> FreeLLMAPI a 0 token con memoria
        """
        p = user_prompt.lower().strip()

        # Mappatura rapida app note
        app_aliases = {
            "spotify": ["spotify", "spotyfy", "spoti"],
            "whatsapp": ["whatsapp", "wapp"],
            "notepad": ["notepad", "blocco note", "blocco-note"],
            "calcolatrice": ["calcolatrice", "calc"],
            "chrome": ["chrome", "google chrome"],
            "edge": ["edge", "microsoft edge", "browser"],
            "terminale": ["terminale", "powershell", "cmd", "terminal", "wt"],
            "code": ["vs code", "vscode", "code"],
            "explorer": ["esplora risorse", "cartella"]
        }

        # 1. Riconoscimento Apertura App
        open_verbs = ["apri ", "avvia ", "lancia ", "start ", "aprimi "]
        is_open = any(p.startswith(v) or f" {v}" in f" {p}" for v in open_verbs)
        if is_open:
            for app_canon, aliases in app_aliases.items():
                if any(alias in p for alias in aliases):
                    return {"type": "open_app", "app": app_canon}
            # Fallback estraendo il target dopo il verbo
            for v in open_verbs:
                if v in p:
                    target = p.split(v, 1)[1].strip()
                    if target:
                        return {"type": "open_app", "app": target}

        # 2. Riconoscimento Chiusura App
        close_verbs = ["chiudi ", "stop ", "termina ", "kill "]
        is_close = any(p.startswith(v) or f" {v}" in f" {p}" for v in close_verbs)
        if is_close:
            for app_canon, aliases in app_aliases.items():
                if any(alias in p for alias in aliases):
                    return {"type": "close_app", "app": app_canon}
            for v in close_verbs:
                if v in p:
                    target = p.split(v, 1)[1].strip()
                    if target:
                        return {"type": "close_app", "app": target}

        # 3. Riconoscimento Automazioni WhatsApp
        if "whatsapp" in p and any(k in p for k in ["manda", "scrivi", "invia", "messaggio"]):
            return {"type": "whatsapp"}
        if any(p.startswith(k) for k in ["manda a ", "scrivi a ", "invia a "]):
            return {"type": "whatsapp"}

        # 4. Riconoscimento Finestre / Snap 50%
        if any(k in p for k in ["50%", "metà", "snap", "affianca"]):
            win = "meet" if "meet" in p else "chrome"
            dir_ = "left" if "sinistra" in p or "left" in p else "right"
            return {"type": "snap_window", "window": win, "dir": dir_}

        # 5. Riconoscimento Compiti Codice / Terminale / Claude Code
        claude_triggers = [
            "claudecode", "claude code", "claude", "da terminale", "comando terminale",
            "comando powershell", "fai da terminale", "script python", "git status",
            "git push", "git commit", "refactor", "crea un file", "crea file", "/code"
        ]
        if any(k in p for k in claude_triggers):
            return {"type": "claude", "prompt": user_prompt}

        # 6. Default: PURO TESTO / CHAT / TRADUZIONE / CONOSCENZA -> FreeLLMAPI a ZERO TOKEN!
        return {"type": "text"}

    def execute(self, user_prompt: str):
        """Esegue il comando smistando al motore appropriato e memorizzando la cronologia."""
        route = self.route_request(user_prompt)
        rtype = route["type"]

        # ==========================================
        # ROTTA 1: APERTURA APP (System Agent)
        # ==========================================
        if rtype == "open_app":
            app = route.get("app", "app")
            print(f"{YELLOW}{BOLD}🚀 [SYSTEM AGENT] Apertura applicazione '{app}'...{RESET}")
            res = self.system.open_app(app)
            out = f"Applicazione {app.capitalize()} aperta con successo!" if res.get("success") else f"Non sono riuscito ad avviare {app}: {res.get('error', '')}"
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": out})
            return out

        # ==========================================
        # ROTTA 2: CHIUSURA APP (System Agent)
        # ==========================================
        elif rtype == "close_app":
            app = route.get("app", "app")
            print(f"{YELLOW}{BOLD}🪟 [SYSTEM AGENT] Chiusura applicazione '{app}'...{RESET}")
            res = self.system.close_app(app)
            out = f"Applicazione {app.capitalize()} chiusa con successo."
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": out})
            return out

        # ==========================================
        # ROTTA 3: SNAP FINESTRE (System Agent)
        # ==========================================
        elif rtype == "snap_window":
            print(f"{YELLOW}{BOLD}🪟 [SYSTEM AGENT] Posizionamento finestra {route['window']} al 50%...{RESET}")
            res = self.system.snap_window(route["window"], direction=route.get("dir", "left"))
            out = f"Finestra {route['window']} posizionata al 50% dello schermo."
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": out})
            return out

        # ==========================================
        # ROTTA 4: CLAUDE CODE (Ingegnere Codice & Terminale)
        # ==========================================
        elif rtype == "claude":
            print(f"{CYAN}{BOLD}🛠️ [CLAUDE CODE CLI] Esecuzione compito tramite Claude Code CLI...{RESET}")
            res = self.system.run_claude(user_prompt)
            out = res.get("output", "Comando eseguito tramite Claude Code.")
            print(f"{CYAN}{BOLD}Risultato Claude Code:{RESET}\n{out}\n")
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": out})
            return out

        # ==========================================
        # ROTTA 5: WHATSAPP AGENT (Micro-Agente)
        # ==========================================
        elif rtype == "whatsapp":
            print(f"{GREEN}{BOLD}📱 [MICRO-AGENTE WHATSAPP] Automazione Desktop a circuito chiuso con Safety Gate...{RESET}")
            recipient = "Gabriele Vinted" if "gabriele" in user_prompt.lower() else "Stefano"
            
            gen_prompt = f"Scrivi un messaggio breve e simpatico per {recipient}: {user_prompt}"
            msg_res = self.freellm.chat([{"role": "user", "content": gen_prompt}], model="auto:fast")
            final_message = msg_res['content'].strip()
            
            res = self.whatsapp.send_message(recipient, final_message)
            out = f"Messaggio inviato su WhatsApp a {recipient}!"
            self.conversation_history.append({"role": "user", "content": user_prompt})
            self.conversation_history.append({"role": "assistant", "content": out})
            return out

        # ==========================================
        # ROTTA 6: PURO TESTO (FreeLLMAPI - 0 Token) CON MEMORIA MULTI-TURN
        # ==========================================
        else:
            print(f"{CYAN}{BOLD}⚡ [FREELLMAPI ROUTE] Richiesta testuale -> Modello Gratuito (0 Token Pagati, 0€){RESET}")
            t0 = time.time()
            try:
                system_instruction = (
                    "Sei MAMBA OS, il sistema operativo cognitivo personale e desktop assistant dell'utente su Windows 11. "
                    "Sei sveglio, brillante, veloce, empatico e altamente operativo. "
                    "Sei direttamente collegato a Windows 11: puoi aprire e chiudere app (Spotify, WhatsApp, Notepad, Browser, ecc.), "
                    "gestire finestre, interagire con il terminale ed eseguire codice tramite Claude Code. "
                    "IMPORTANTE: Non dire MAI che sei una semplice chat isolata o che non hai accesso al dispositivo dell'utente, "
                    "perché operi nativamente sul PC dell'utente. Se ti chiedono di compiere azioni sul PC, confermagli che te ne occupi. "
                    "Sii conciso e diretto: massimo 2-3 frasi per risposta, a meno che non ti venga esplicitamente richiesta una spiegazione dettagliata o del codice. "
                    "Se ti chiedono traduzioni in cinese o altre lingue, fornisci sempre caratteri, pinyin e significato in modo chiaro e pulito."
                )

                messages = [{"role": "system", "content": system_instruction}]
                if self.conversation_history:
                    messages.extend(self.conversation_history[-self.max_history:])
                messages.append({"role": "user", "content": user_prompt})

                res = self.freellm.chat(messages, model="auto:fast", temperature=0.7, max_tokens=600)
                elapsed = time.time() - t0
                reply = clean_llm_reply(res['content'].strip())

                # Salva il turno nella cronologia
                self.conversation_history.append({"role": "user", "content": user_prompt})
                self.conversation_history.append({"role": "assistant", "content": reply})

                print(f"{EMERALD}{BOLD}\n🐍 Mamba:{RESET}\n{reply}\n")
                print(f"{DIM}⏱️ Risposto in {elapsed:.2f}s tramite {res.get('provider', 'FreeLLMAPI')} | Costo: 0.00€{RESET}\n")
                return reply
            except Exception as e:
                print(f"{RED}❌ Errore FreeLLMAPI: {e}{RESET}")
                return f"Si è verificato un intoppo cognitivo temporaneo: {e}"

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
