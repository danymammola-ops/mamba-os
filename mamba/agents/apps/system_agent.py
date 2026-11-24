#!/usr/bin/env python3
"""
mamba/agents/apps/system_agent.py - Micro-Agente Sistema, Terminale, App Launcher & Claude Code Bridge
"""

from __future__ import annotations

import ctypes
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Optional

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.moves.user_moves import attach_to_user_desktop, get_screen_size

attach_to_user_desktop()
import uiautomation as auto

MAMBA_ROOT = r"C:\Users\danym\mio\mamba"
VAULT_ROOT = os.environ.get("OBSIDIAN_VAULT_PATH", r"C:\Users\danym\Documents\ObsidianVault")


class SystemAgent:
    def __init__(self):
        attach_to_user_desktop()
        self.user32 = ctypes.windll.user32

    def open_app(self, app_name: str) -> dict:
        """Apre applicazioni Windows, URL, cartelle o tool di sviluppo."""
        attach_to_user_desktop()
        app_clean = app_name.lower().strip()

        # URL diretto o percorso esistente
        if app_clean.startswith(("http://", "https://", "obsidian://", "whatsapp://")):
            os.startfile(app_name.strip())  # type: ignore[attr-defined]
            return {"success": True, "app": app_name, "command": f"open {app_name}"}

        app_map = {
            "spotify": "start spotify:",
            "spotyfy": "start spotify:",
            "whatsapp": "start whatsapp:",
            "obsidian": 'start "" "obsidian://open?vault=ObsidianVault"',
            "galaxy": 'start "" "http://127.0.0.1:5173/galaxy.html"',
            "github": 'start "" "https://github.com/danymammola-ops/mamba-os"',
            "youtube": 'start "" "https://www.youtube.com"',
            "claude": 'start "" "https://claude.ai"',
            "chatgpt": 'start "" "https://chatgpt.com"',
            "vault": f'explorer "{VAULT_ROOT}"',
            "cervello": f'explorer "{VAULT_ROOT}"',
            "mamba": f'code "{MAMBA_ROOT}"',
            "freellmapi": r'start "" "c:\Users\danym\Desktop\Dany\mio\ai\freellmapi\start-freellmapi.bat"',
            "notepad": "start notepad",
            "blocco note": "start notepad",
            "calc": "start calc",
            "calcolatrice": "start calc",
            "chrome": "start chrome",
            "google chrome": "start chrome",
            "edge": "start msedge",
            "microsoft edge": "start msedge",
            "terminal": "start wt",
            "terminale": "start wt",
            "powershell": "start powershell",
            "cmd": "start cmd",
            "code": "start code",
            "vs code": "start code",
            "vscode": "start code",
            "explorer": "start explorer",
            "esplora risorse": "start explorer",
        }

        cmd = app_map.get(app_clean)
        if not cmd:
            for key, mapped in app_map.items():
                if key in app_clean:
                    cmd = mapped
                    break
        if not cmd:
            cmd = f'start "" "{app_clean}"'

        try:
            subprocess.Popen(cmd, shell=True)
            return {"success": True, "app": app_name, "command": cmd}
        except Exception as e:
            return {"success": False, "app": app_name, "error": str(e)}

    def run_command(self, cmd: str, cwd: Optional[str] = None) -> dict:
        """Esegue un comando PowerShell e cattura l'output."""
        work_dir = cwd if (cwd and os.path.isdir(cwd)) else MAMBA_ROOT
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-Command", cmd],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=30,
                encoding="utf-8",
                errors="replace",
            )
            return {
                "success": res.returncode == 0,
                "stdout": res.stdout.strip(),
                "stderr": res.stderr.strip(),
                "code": res.returncode,
                "cwd": work_dir,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Timeout comando terminale (>30s)", "cwd": work_dir}
        except Exception as e:
            return {"success": False, "error": str(e), "cwd": work_dir}

    def run_claude(self, prompt: str, brain_context: str = "", cwd: Optional[str] = None) -> dict:
        """Esegue Claude Code CLI in background con accesso a file, terminale e contesto Secondo Cervello."""
        work_dir = cwd if (cwd and os.path.isdir(cwd)) else (
            VAULT_ROOT if any(k in prompt.lower() for k in ("vault", "obsidian", "cervello", "nota")) else MAMBA_ROOT
        )
        claude_bin = shutil.which("claude.cmd") or shutil.which("claude") or "claude"

        full_prompt = prompt.strip()
        if brain_context:
            full_prompt = (
                f"[CONTESTO SECONDO CERVELLO DI DANIELE]:\n{brain_context[:1800]}\n\n"
                f"[RICHIESTA OPERATIVA (puoi usare terminale, file e aprire app Windows con powershell/start)]:\n{prompt.strip()}"
            )

        try:
            # Passa il prompt su stdin con -p per evitare problemi di escaping su Windows
            cmd_list = (
                ["powershell", "-NoProfile", "-Command", "claude -p"]
                if claude_bin.lower().endswith(".ps1")
                else [claude_bin, "-p"]
            )
            res = subprocess.run(
                cmd_list,
                input=full_prompt,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=120,
                encoding="utf-8",
                errors="replace",
            )
            out = res.stdout.strip()
            err = res.stderr.strip()

            filtered = []
            for line in out.splitlines():
                if any(skip in line for skip in (
                    "Permission allow rule",
                    "CLAUDE_CODE_AUTO_COMPACT",
                    "Warning: no stdin",
                    "[claude-code:unrecognized_model]",
                )):
                    continue
                filtered.append(line)

            clean_output = "\n".join(filtered).strip() or out
            if not clean_output and err:
                clean_output = f"Output errore Claude Code:\n{err}"

            return {
                "success": res.returncode == 0,
                "output": clean_output or "Compito completato da Claude Code.",
                "raw_stderr": err,
                "cwd": work_dir,
            }
        except subprocess.TimeoutExpired:
            return {"success": False, "output": "Timeout Claude Code (>120s).", "cwd": work_dir}
        except Exception as e:
            return {"success": False, "output": f"Errore Claude Code: {e}", "cwd": work_dir}

    def close_app(self, app_name: str) -> dict:
        """Chiude un'applicazione per nome finestra o processo."""
        attach_to_user_desktop()
        app_lower = app_name.lower()
        closed_windows = 0

        root = auto.GetRootControl()
        for child in root.GetChildren():
            name = (child.Name or "").lower()
            cls = (child.ClassName or "").lower()
            if app_lower in name or app_lower in cls:
                hwnd = child.NativeWindowHandle
                self.user32.PostMessageW(hwnd, 0x0010, 0, 0)
                closed_windows += 1

        time.sleep(0.4)
        subprocess.run(["powershell", "-Command", f"Stop-Process -Name '{app_name}' -Force -ErrorAction SilentlyContinue"], capture_output=True)
        return {"success": True, "app": app_name, "windows_closed": closed_windows}

    def snap_window(self, window_keyword: str, direction: str = "left", percent: int = 50) -> dict:
        """Aggancia una finestra e la ridimensiona al 50% dello schermo."""
        attach_to_user_desktop()
        get_screen_size()
        root = auto.GetRootControl()
        target = None
        for child in root.GetChildren():
            name = (child.Name or "").lower()
            if window_keyword.lower() in name:
                target = child
                break
        if not target:
            return {"success": False, "error": f"Nessuna finestra trovata per '{window_keyword}'"}

        hwnd = target.NativeWindowHandle
        self.user32.ShowWindow(hwnd, 9)
        time.sleep(0.2)
        self.user32.SetForegroundWindow(hwnd)
        time.sleep(0.25)

        hotkey_dir = "left" if direction == "left" else "right"
        pyautogui.hotkey("win", hotkey_dir)
        time.sleep(0.35)
        pyautogui.press("esc")
        rect = target.BoundingRectangle
        return {"success": True, "window": target.Name, "rect": (rect.left, rect.top, rect.width(), rect.height())}
