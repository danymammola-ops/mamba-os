#!/usr/bin/env python3
"""
mamba/ui/server.py - Server Multi-Thread HTTP & API per MAMBA OS v2.0
Gestisce concorrentemente:
- HUD Web & Galaxy 3D (/ , /galaxy.html)
- Command Router (/api/command) con FreeLLMAPI + Secondo Cervello + Claude Code
- Neural Italian TTS (/api/tts) via Edge-TTS
- Mini & Pets single-instance PID manager (/api/pet/config, /api/pet/action)
- Claude Code & Terminal Bridge (/api/claude, /api/terminal)
- Second Brain Graph/Search/Note/Gardener (/api/brain/*)
- GitHub Repo Status & Sync (/api/github/*)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.parse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict

sys.path.insert(0, r"C:\Users\danym\mio\mamba")
from mamba.console import MambaConsole
from mamba.voice.tts_engine import AVAILABLE_VOICES, synthesize_speech

UI_DIR = Path(__file__).resolve().parent
MAMBA_ROOT = Path(r"C:\Users\danym\mio\mamba")
PET_CONFIG_FILE = UI_DIR / "pet_config.json"
PET_PID_FILE = UI_DIR / "pet.pid"
PET_SCRIPT = UI_DIR / "desktop_pet.py"

console = MambaConsole()


def _is_pid_running(pid: int) -> bool:
    try:
        res = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/NH"],
            capture_output=True, text=True, timeout=3,
        )
        return str(pid) in (res.stdout or "")
    except Exception:
        return False


def _get_pet_pid() -> int | None:
    if not PET_PID_FILE.exists():
        return None
    try:
        pid = int(PET_PID_FILE.read_text(encoding="utf-8").strip())
        if _is_pid_running(pid):
            return pid
        PET_PID_FILE.unlink(missing_ok=True)
    except Exception:
        pass
    return None


def _ensure_pet_state(enabled: bool) -> bool:
    pid = _get_pet_pid()
    if enabled:
        if pid is None and PET_SCRIPT.exists():
            subprocess.Popen(
                [sys.executable, str(PET_SCRIPT)],
                cwd=str(UI_DIR),
                creationflags=0x00000008,  # DETACHED_PROCESS
            )
        return True
    else:
        if pid is not None:
            subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True)
            PET_PID_FILE.unlink(missing_ok=True)
        return False


def _load_pet_config() -> Dict[str, Any]:
    default_cfg: Dict[str, Any] = {
        "enabled": True,
        "skin": "emerald",
        "style": "pixel",
        "size": "medium",
        "opacity": 0.96,
        "show_on_all": True,
        "show_on_desktop": True,
        "show_on_whatsapp": True,
        "show_on_spotify": True,
        "show_on_browser": True,
        "show_on_notepad": True,
        "show_on_vscode": True,
        "show_on_obsidian": True,
        "animated_tongue": True,
        "speaking_sway": True,
        "slither_idle": True,
        "bubble_enabled": True,
    }
    if PET_CONFIG_FILE.exists():
        try:
            default_cfg.update(json.loads(PET_CONFIG_FILE.read_text(encoding="utf-8")))
        except Exception:
            pass
    default_cfg["running"] = _get_pet_pid() is not None
    return default_cfg


def _git_run(args):
    return subprocess.run(
        ["git"] + args,
        cwd=str(MAMBA_ROOT),
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=20,
    )


class MambaUIHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def log_message(self, format, *args):
        # Silenzia log HTTP rumorosi su console
        pass

    def _send_json(self, status: int, data: Any) -> None:
        raw = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(raw)

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/brain/stats":
            stats = console.brain.get_stats() if getattr(console, "brain", None) else {"available": False}
            return self._send_json(200, stats)

        if path == "/api/brain/search":
            qs = urllib.parse.parse_qs(parsed.query)
            q = (qs.get("q") or [""])[0]
            hits = console.brain.search(q, limit=8) if getattr(console, "brain", None) else []
            return self._send_json(200, {"query": q, "results": hits})

        if path == "/api/brain/graph":
            graph = console.brain.get_graph() if getattr(console, "brain", None) else {"nodes": [], "edges": []}
            return self._send_json(200, graph)

        if path == "/api/brain/note":
            qs = urllib.parse.parse_qs(parsed.query)
            note_ref = (qs.get("path") or [""])[0]
            note = console.brain.read_note(note_ref) if getattr(console, "brain", None) else None
            return self._send_json(200 if note else 404, note or {"error": "Not found"})

        if path == "/api/tts/voices":
            return self._send_json(200, {"voices": AVAILABLE_VOICES})

        if path == "/api/pet/config":
            return self._send_json(200, _load_pet_config())

        if path == "/api/github/status":
            branch = (_git_run(["branch", "--show-current"]).stdout or "main").strip()
            remote = (_git_run(["remote", "get-url", "origin"]).stdout or "").strip()
            status_lines = [l for l in _git_run(["status", "--short"]).stdout.splitlines() if l.strip()]
            last_commits = [l for l in _git_run(["log", "-n", "5", "--oneline"]).stdout.splitlines() if l.strip()]
            return self._send_json(200, {
                "branch": branch,
                "remote": remote,
                "dirty_count": len(status_lines),
                "changed_files": status_lines[:25],
                "recent_commits": last_commits,
            })

        if path == "/api/system/status":
            models = console.freellm.get_ready_models() if console.freellm else []
            return self._send_json(200, {
                "freellm_online": len(models) > 0,
                "freellm_url": console.freellm.base_url if console.freellm else "",
                "ready_models": len(models),
                "brain_available": bool(console.brain and console.brain.available),
                "history_len": len(console.conversation_history),
            })

        return super().do_GET()

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/api/command":
            try:
                data = self._read_json()
                prompt = (data.get("prompt") or "").strip()
                mode = (data.get("mode") or "auto").strip()
                route_info = console.route_request(prompt, mode=mode)
                out = console.execute(prompt, mode=mode)
                return self._send_json(200, {
                    "success": True,
                    "output": str(out or "Comando eseguito."),
                    "route": route_info["type"],
                })
            except Exception as exc:
                return self._send_json(200, {"success": False, "error": str(exc), "route": "error"})

        if path == "/api/chat/clear":
            console.clear_history()
            return self._send_json(200, {"success": True})

        if path == "/api/tts":
            try:
                data = self._read_json()
                text = (data.get("text") or "").strip()
                voice = (data.get("voice") or "it-IT-GiuseppeMultilingualNeural").strip()
                rate = (data.get("rate") or "+4%").strip()
                audio_bytes = synthesize_speech(text, voice=voice, rate=rate)
                self.send_response(200)
                self.send_header("Content-Type", "audio/mpeg")
                self.send_header("Content-Length", str(len(audio_bytes)))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(audio_bytes)
                return
            except Exception as exc:
                return self._send_json(502, {"success": False, "error": str(exc)})

        if path == "/api/pet/config":
            try:
                new_cfg = self._read_json()
                cur_cfg = _load_pet_config()
                cur_cfg.pop("running", None)
                cur_cfg.update(new_cfg)
                PET_CONFIG_FILE.write_text(json.dumps(cur_cfg, indent=2), encoding="utf-8")
                _ensure_pet_state(bool(cur_cfg.get("enabled", True)))
                cur_cfg["running"] = _get_pet_pid() is not None
                return self._send_json(200, {"success": True, "config": cur_cfg})
            except Exception as exc:
                return self._send_json(500, {"success": False, "error": str(exc)})

        if path == "/api/pet/action":
            try:
                data = self._read_json()
                action = data.get("action")
                cur_cfg = _load_pet_config()
                cur_cfg.pop("running", None)
                if action == "wave":
                    cur_cfg["wave_until"] = time.time() + 2.5
                    cur_cfg["enabled"] = True
                elif action == "recenter":
                    cur_cfg["recenter"] = True
                    cur_cfg["enabled"] = True
                PET_CONFIG_FILE.write_text(json.dumps(cur_cfg, indent=2), encoding="utf-8")
                _ensure_pet_state(True)
                return self._send_json(200, {"success": True, "action": action})
            except Exception as exc:
                return self._send_json(500, {"success": False, "error": str(exc)})

        if path == "/api/terminal":
            try:
                data = self._read_json()
                cmd = (data.get("cmd") or "").strip()
                cwd = data.get("cwd") or None
                if not cmd:
                    return self._send_json(400, {"success": False, "error": "Comando vuoto"})
                res = console.system.run_command(cmd, cwd=cwd)
                return self._send_json(200, res)
            except Exception as exc:
                return self._send_json(500, {"success": False, "error": str(exc)})

        if path == "/api/claude":
            try:
                data = self._read_json()
                prompt = (data.get("prompt") or "").strip()
                cwd = data.get("cwd") or None
                if not prompt:
                    return self._send_json(400, {"success": False, "error": "Prompt vuoto"})
                brain_ctx = console.brain.get_context_snippet(prompt, max_chars=1800) if (console.brain and console.brain.available) else ""
                res = console.system.run_claude(prompt, brain_context=brain_ctx, cwd=cwd)
                return self._send_json(200, res)
            except Exception as exc:
                return self._send_json(500, {"success": False, "error": str(exc)})

        if path == "/api/brain/gardener":
            try:
                if console.brain and console.brain.engine_dir.exists():
                    sys.path.insert(0, str(console.brain.engine_dir))
                    from gardener import run_gardener  # type: ignore
                    res = run_gardener(console.brain.vault_path)
                    return self._send_json(200, {"success": True, "result": res})
                return self._send_json(404, {"success": False, "error": "Brain engine non trovato"})
            except Exception as exc:
                return self._send_json(500, {"success": False, "error": str(exc)})

        if path == "/api/github/push":
            try:
                data = self._read_json()
                msg = (data.get("message") or f"chore(mamba): sync HUD, Second Brain, Voice & MiniPet [{time.strftime('%Y-%m-%d %H:%M')}]").strip()
                _git_run(["add", "-A"])
                commit_res = _git_run(["commit", "-m", msg])
                push_res = _git_run(["push"])
                return self._send_json(200, {
                    "success": push_res.returncode == 0,
                    "commit_out": (commit_res.stdout + "\n" + commit_res.stderr).strip(),
                    "push_out": (push_res.stdout + "\n" + push_res.stderr).strip(),
                })
            except Exception as exc:
                return self._send_json(500, {"success": False, "error": str(exc)})

        return self._send_json(404, {"error": "Endpoint not found"})


def run_server(port: int = 5173):
    server_address = ("127.0.0.1", port)
    try:
        httpd = ThreadingHTTPServer(server_address, MambaUIHandler)
    except OSError:
        print(f"ℹ️ [MAMBA OS HUD] Server già attivo su http://127.0.0.1:{port}")
        return

    print(f"🐍 [MAMBA OS v2.0] Server multi-thread attivo su: http://127.0.0.1:{port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    run_server()
