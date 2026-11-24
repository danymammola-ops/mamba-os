#!/usr/bin/env python3
"""
mamba/console.py - Console di Collegamento & Smart Router Gateway per MAMBA OS v2.0
Instrada in modo rapido ed efficiente tra:
1. Azioni Dirette Desktop (Apri/Chiudi App, URL, Cartelle, Window Snap)
2. Secondo Cervello Obsidian (<20ms FTS5 + Graph)
3. Claude Code + Terminale (con contesto reale dal Secondo Cervello)
4. Micro-Agente WhatsApp con Safety Gate
5. FreeLLMAPI locale (0€, arricchito dal Secondo Cervello + memoria conversazionale)
"""

from __future__ import annotations

import re
import sys
import time
from typing import Any, Dict

GREEN = "\033[92m"
EMERALD = "\033[38;2;0;255;136m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.agents.apps.system_agent import SystemAgent
from mamba.agents.apps.whatsapp_agent import WhatsAppAgent
from mamba.core.freellm_client import FreeLLMClient

try:
    from mamba.core.brain_bridge import BrainBridge
except Exception:
    BrainBridge = None


def clean_llm_reply(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    if "Here's a thinking process:" in text:
        parts = text.split("Here's a thinking process:")
        after = parts[-1]
        lines = [
            line for line in after.splitlines()
            if not line.strip().startswith(("*", "-", "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."))
            and line.strip()
        ]
        if lines:
            text = "\n".join(lines[-4:]).strip()
    return text.strip()


class MambaConsole:
    def __init__(self):
        self.freellm = FreeLLMClient()
        self.whatsapp = WhatsAppAgent()
        self.system = SystemAgent()
        self.brain = BrainBridge() if BrainBridge else None
        self.session_tokens_saved = 0
        self.conversation_history = []
        self.max_history = 14

    def clear_history(self):
        self.conversation_history.clear()

    def route_request(self, user_prompt: str, mode: str = "auto") -> Dict[str, Any]:
        p = user_prompt.lower().strip()
        mode_clean = (mode or "auto").lower().strip()

        if mode_clean == "claude":
            return {"type": "claude", "prompt": user_prompt}
        if mode_clean == "terminal":
            return {"type": "terminal", "cmd": user_prompt}
        if mode_clean == "brain" and self.brain and self.brain.available:
            act = self.brain.detect_brain_action(user_prompt)
            if act:
                return {"type": "brain", "action_info": act}
            return {"type": "brain_search", "query": user_prompt}
        if mode_clean == "chat":
            return {"type": "text"}

        # 1. Apertura App / URL / Cartelle
        app_aliases = {
            "spotify": ["spotify", "spotyfy", "spoti"],
            "whatsapp": ["whatsapp", "wapp"],
            "obsidian": ["obsidian"],
            "galaxy": ["galaxy", "galassia"],
            "github": ["github", "repo"],
            "youtube": ["youtube"],
            "claude": ["claude.ai", "sito claude"],
            "freellmapi": ["freellmapi", "gateway llm"],
            "vault": ["cartella vault", "il vault", "secondo cervello"],
            "notepad": ["notepad", "blocco note", "blocco-note"],
            "calcolatrice": ["calcolatrice", "calc"],
            "chrome": ["chrome", "google chrome"],
            "edge": ["edge", "microsoft edge", "browser"],
            "terminale": ["terminale", "powershell", "cmd", "terminal", "wt"],
            "code": ["vs code", "vscode", "visual studio code"],
            "explorer": ["esplora risorse", "cartella"],
        }
        open_verbs = ["apri ", "avvia ", "lancia ", "start ", "aprimi "]
        if any(p.startswith(v) or f" {v}" in f" {p}" for v in open_verbs):
            for app_canon, aliases in app_aliases.items():
                if any(alias in p for alias in aliases):
                    return {"type": "open_app", "app": app_canon}
            for v in open_verbs:
                if v in p:
                    target = p.split(v, 1)[1].strip()
                    if target:
                        return {"type": "open_app", "app": target}

        # 2. Chiusura App
        close_verbs = ["chiudi ", "stop ", "termina ", "kill "]
        if any(p.startswith(v) or f" {v}" in f" {p}" for v in close_verbs):
            for app_canon, aliases in app_aliases.items():
                if any(alias in p for alias in aliases):
                    return {"type": "close_app", "app": app_canon}

        # 3. Snap 50%
        if any(k in p for k in ["50%", "metà", "snap", "affianca"]):
            win = "meet" if "meet" in p else "chrome"
            dir_ = "left" if "sinistra" in p or "left" in p else "right"
            return {"type": "snap_window", "window": win, "dir": dir_}

        # 4. WhatsApp
        if ("whatsapp" in p and any(k in p for k in ["manda", "scrivi", "invia", "messaggio"])) or any(
            p.startswith(k) for k in ["manda a ", "scrivi a ", "invia a "]
        ):
            return {"type": "whatsapp"}

        # 5. Secondo Cervello diretto
        if self.brain and self.brain.available:
            brain_act = self.brain.detect_brain_action(user_prompt)
            if brain_act:
                return {"type": "brain", "action_info": brain_act}

        # 6. Claude Code & Terminale
        if p.startswith("/sh ") or p.startswith("!"):
            cmd = user_prompt.strip()[4:].strip() if p.startswith("/sh ") else user_prompt.strip()[1:].strip()
            return {"type": "terminal", "cmd": cmd}

        claude_triggers = [
            "claudecode", "claude code", "chiedi a claude", "usa claude", "claude ",
            "da terminale", "comando terminale", "comando powershell", "esegui da terminale",
            "script python", "crea uno script", "crea un file", "crea file", "modifica il codice",
            "sistema il bug", "fixa", "refactor", "git status", "git push", "git commit", "/code",
        ]
        if any(k in p for k in claude_triggers):
            return {"type": "claude", "prompt": user_prompt}

        return {"type": "text"}

    def execute(self, user_prompt: str, mode: str = "auto"):
        route = self.route_request(user_prompt, mode=mode)
        rtype = route["type"]

        if rtype == "open_app":
            app = route.get("app", "app")
            res = self.system.open_app(app)
            out = f"Ho aperto {app}!" if res.get("success") else f"Impossibile avviare {app}: {res.get('error', '')}"

        elif rtype == "close_app":
            app = route.get("app", "app")
            self.system.close_app(app)
            out = f"Applicazione {app.capitalize()} chiusa."

        elif rtype == "snap_window":
            self.system.snap_window(route["window"], direction=route.get("dir", "left"))
            out = f"Finestra {route['window']} affiancata al 50%."

        elif rtype == "terminal":
            res = self.system.run_command(route["cmd"])
            out = res.get("stdout") or res.get("stderr") or res.get("error") or f"Exit code: {res.get('code')}"

        elif rtype == "claude":
            brain_ctx = self.brain.get_context_snippet(user_prompt, max_chars=1600) if (self.brain and self.brain.available) else ""
            res = self.system.run_claude(route["prompt"], brain_context=brain_ctx)
            out = res.get("output", "Compito completato da Claude Code.")

        elif rtype == "whatsapp":
            recipient = "Gabriele Vinted" if "gabriele" in user_prompt.lower() else "Stefano"
            gen_prompt = f"Scrivi un messaggio breve, naturale e simpatico per {recipient}: {user_prompt}"
            msg_res = self.freellm.chat([{"role": "user", "content": gen_prompt}], model="auto:fast")
            self.whatsapp.send_message(recipient, msg_res["content"].strip())
            out = f"Messaggio inviato su WhatsApp a {recipient}!"

        elif rtype == "brain" and self.brain:
            out = self.brain.execute_brain_action(route["action_info"])

        elif rtype == "brain_search" and self.brain:
            hits = self.brain.search(route["query"], limit=5)
            if not hits:
                out = f"Nessuna nota trovata nel Secondo Cervello per '{route['query']}'."
            else:
                lines = [f"- **{h['title']}** (`{h['path']}`): {h['summary'] or h['snippet']}" for h in hits]
                out = "Risultati dal Secondo Cervello:\n" + "\n".join(lines)

        else:
            try:
                brain_ctx = self.brain.get_context_snippet(user_prompt, max_chars=2200) if (self.brain and self.brain.available) else ""
                system_instruction = (
                    "Sei MAMBA OS, il sistema operativo cognitivo personale di Daniele Mammola (Dany) su Windows 11. "
                    "Sei rapido, brillante, diretto e operativo, mai prolisso o cerimonioso. "
                    "Sei connesso al suo PC Windows 11, al suo Secondo Cervello Obsidian, a Claude Code e alle sue app. "
                    "Rispondi in italiano naturale e diretto (max 2-4 frasi, salvo quando ti chiede codice o dettagli)."
                )
                if brain_ctx:
                    system_instruction += f"\n\n[CONTESTO DAL SECONDO CERVELLO DI DANIELE]:\n{brain_ctx}"

                messages = [{"role": "system", "content": system_instruction}]
                if self.conversation_history:
                    messages.extend(self.conversation_history[-self.max_history:])
                messages.append({"role": "user", "content": user_prompt})

                res = self.freellm.chat(messages, model="auto:fast", temperature=0.65, max_tokens=650)
                out = clean_llm_reply(res["content"].strip())
            except Exception as e:
                # Fallback intelligente locale usando i dati del Secondo Cervello se FreeLLMAPI è spento
                if self.brain and self.brain.available:
                    hits = self.brain.search(user_prompt, limit=3)
                    if hits:
                        out = (
                            "FreeLLMAPI è offline su 127.0.0.1:31415, ma ho trovato queste note nel tuo Secondo Cervello:\n"
                            + "\n".join(f"- {h['title']} ({h['path']}): {h['summary'] or h['snippet']}" for h in hits)
                        )
                    else:
                        out = f"FreeLLMAPI offline su 127.0.0.1:31415 (avvialo con start-freellmapi.bat). Errore: {e}"
                else:
                    out = f"Errore FreeLLMAPI: {e}"

        self.conversation_history.append({"role": "user", "content": user_prompt})
        self.conversation_history.append({"role": "assistant", "content": out})
        return out
