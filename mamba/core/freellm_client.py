#!/usr/bin/env python3
"""
mamba/core/freellm_client.py - Client asincrono e sincrono per FreeLLMAPI
Gestisce:
- Auto-discovery di porta e token dal database locale SQLite (%APPDATA%/FreeLLMAPI/freeapi.db).
- Rotazione e failover automatico (timeout 15s) verso modelli ultra-veloci (auto:fast).
- Tracciamento in tempo reale del provider attivo (header X-Routed-Via).
- Zero dipendenze obbligatorie (funziona con standard library urllib e json).
"""

import os
import sys
import json
import sqlite3
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Generator, Tuple

def get_freellm_dir() -> str:
    """Restituisce il percorso della cartella dati di FreeLLMAPI su Windows/Mac/Linux."""
    if sys.platform == "win32":
        return os.path.join(os.environ.get("APPDATA", os.path.expanduser("~\\AppData\\Roaming")), "FreeLLMAPI")
    elif sys.platform == "darwin":
        return os.path.expanduser("~/Library/Application Support/FreeLLMAPI")
    return os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config/FreeLLMAPI"))

def discover_credentials() -> Tuple[str, str]:
    """
    Rileva automaticamente porta e unified API key dal sistema locale.
    Priorità:
    1. Variabili d'ambiente (FREELLM_URL, FREELLM_API_KEY, ANTHROPIC_AUTH_TOKEN)
    2. Database SQLite locale di FreeLLMAPI (freeapi.db)
    3. Default (http://127.0.0.1:31415, porta configurata)
    """
    base_url = os.environ.get("FREELLM_URL", "")
    api_key = os.environ.get("FREELLM_API_KEY", "") or os.environ.get("ANTHROPIC_AUTH_TOKEN", "")

    app_dir = get_freellm_dir()
    db_path = os.path.join(app_dir, "freeapi.db")
    config_path = os.path.join(app_dir, "config.json")

    # Leggi porta da config.json se presente
    port = 31415
    if os.path.exists(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
                port = int(cfg.get("port") or cfg.get("serverPort") or 31415)
        except Exception:
            pass

    if not base_url:
        base_url = f"http://127.0.0.1:{port}/v1"

    # Se la chiave non è in env, leggila da SQLite
    if not api_key and os.path.exists(db_path):
        try:
            conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM settings WHERE key = 'unified_api_key' LIMIT 1")
            row = cursor.fetchone()
            if row and row[0]:
                api_key = str(row[0]).strip()
            conn.close()
        except Exception:
            pass

    return base_url.rstrip("/"), api_key

class FreeLLMClient:
    def __init__(self, base_url: Optional[str] = None, api_key: Optional[str] = None):
        discovered_url, discovered_key = discover_credentials()
        self.base_url = (base_url or discovered_url).rstrip("/")
        self.api_key = api_key or discovered_key
        self.last_provider = "UNKNOWN"
        self.last_latency = 0.0

    def get_ready_models(self) -> List[str]:
        """Restituisce la lista di modelli pronti all'uso su FreeLLMAPI."""
        url = f"{self.base_url}/models?execution_status=ready"
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        req = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                models = [m["id"] for m in data.get("data", [])]
                return models
        except Exception as e:
            print(f"⚠️ [Mamba FreeLLM] Errore verifica modelli: {e}")
            return []

    def chat(self, messages: List[Dict[str, str]], model: str = "auto", temperature: float = 0.7, timeout: int = 15) -> Dict[str, Any]:
        """
        Invia una richiesta di chat a FreeLLMAPI con failover automatico se lento.
        Restituisce un dizionario con {'content': str, 'provider': str, 'latency': float}.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": False
        }
        data = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        start_time = time.time()
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")

        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                elapsed = time.time() - start_time
                self.last_latency = round(elapsed, 2)
                self.last_provider = resp.headers.get("X-Routed-Via", "FreeLLMAPI")
                body = json.loads(resp.read().decode("utf-8"))
                choice = body.get("choices", [{}])[0]
                content = choice.get("message", {}).get("content", "")
                return {
                    "content": content,
                    "provider": self.last_provider,
                    "latency": self.last_latency,
                    "raw": body
                }
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"⚠️ [Mamba FreeLLM] Modello {model} lento o non raggiungibile ({e}). Failover su 'auto:fast'...")
            # Fallback immediato su auto:fast
            if model != "auto:fast":
                return self.chat(messages, model="auto:fast", temperature=temperature, timeout=12)
            raise e

    def stream_chat(self, messages: List[Dict[str, str]], model: str = "auto", temperature: float = 0.7) -> Generator[str, None, None]:
        """
        Streaming in tempo reale token-per-token.
        Emette i delta di testo appena arrivano.
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": True
        }
        data = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=30) as resp:
            self.last_provider = resp.headers.get("X-Routed-Via", "FreeLLMAPI")
            for line in resp:
                line_str = line.decode("utf-8").strip()
                if not line_str or line_str.startswith(":"):
                    continue
                if line_str.startswith("data: "):
                    content = line_str[6:].strip()
                    if content == "[DONE]":
                        break
                    try:
                        chunk = json.loads(content)
                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            yield delta
                    except json.JSONDecodeError:
                        continue

if __name__ == "__main__":
    client = FreeLLMClient()
    print(f"🐍 [Mamba Core] Connesso a: {client.base_url}")
    print(f"🔑 [Mamba Core] Chiave rilevata: {client.api_key[:12]}...")
    models = client.get_ready_models()
    print(f"📦 [Mamba Core] Modelli disponibili: {len(models)}")
    
    print("\n🧪 [Test Chat Streaming su Gemini/Auto]:")
    res = client.chat([{"role": "user", "content": "Dimmi una frase breve in stile Mamba: veloce, precisa e potente."}])
    print(f"Risposta: {res['content']}")
    print(f"Provider: {res['provider']} ({res['latency']}s)")
