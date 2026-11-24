#!/usr/bin/env python3
"""
mamba/core/brain_bridge.py - Ponte operativo tra MAMBA OS e il Secondo Cervello Obsidian.
Permette a Mamba di:
1. Leggere contesto reale di Daniele (chi-sono, tono, progetti, decisioni, diario) in <20ms.
2. Salvare appunti, ricordi e note giornaliere direttamente nel Vault da chat/voce.
3. Sincronizzare le compattazioni del Token Guard verso 00_Inbox/Pending_Approval/.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

VAULT_PATH = Path(os.environ.get("OBSIDIAN_VAULT_PATH", r"C:\Users\danym\Documents\ObsidianVault"))
ENGINE_DIR = VAULT_PATH / "90_System" / "brain_engine"


class BrainBridge:
    def __init__(self, vault_path: Optional[Path] = None):
        self.vault_path = Path(vault_path) if vault_path else VAULT_PATH
        self.engine_dir = self.vault_path / "90_System" / "brain_engine"
        self.store = None
        self._load_store()

    def _load_store(self) -> None:
        try:
            if self.engine_dir.exists() and str(self.engine_dir) not in sys.path:
                sys.path.insert(0, str(self.engine_dir))
            from vault_index import BrainStore  # type: ignore

            self.store = BrainStore(self.vault_path)
            self.store.sync_index()
        except Exception:
            self.store = None

    @property
    def available(self) -> bool:
        return self.store is not None

    def get_stats(self) -> Dict[str, Any]:
        if not self.store:
            return {"available": False, "total_notes": 0, "total_links": 0}
        try:
            lint = self.store.lint_graph()
            return {
                "available": True,
                "vault": str(self.vault_path),
                "total_notes": lint["total_notes"],
                "total_links": lint["total_links"],
                "orphans": len(lint["orphan_notes"]),
                "broken_links": len(lint["broken_links"]),
                "pending_approval": len(lint["pending_approval_items"]),
                "top_hubs": lint["top_hubs"][:5],
            }
        except Exception as exc:
            return {"available": False, "error": str(exc)}

    def search(self, query: str, limit: int = 5):
        if not self.store or not query.strip():
            return []
        try:
            return self.store.search(query, limit=limit)
        except Exception:
            return []

    def get_graph(self) -> Dict[str, Any]:
        if not self.store:
            return {"nodes": [], "edges": [], "total_notes": 0, "total_edges": 0}
        try:
            return self.store.get_graph_data()
        except Exception as exc:
            return {"nodes": [], "edges": [], "error": str(exc)}

    def read_note(self, path_or_stem: str) -> Optional[Dict[str, Any]]:
        if not self.store or not path_or_stem.strip():
            return None
        try:
            return self.store.read_note(path_or_stem)
        except Exception:
            return None

    def get_context_snippet(self, prompt: str, max_chars: int = 4200) -> str:
        if not self.store:
            return ""
        try:
            pack = self.store.build_context_pack(prompt, max_chars=max_chars)
            return pack.get("context_text", "")
        except Exception:
            return ""

    def detect_brain_action(self, prompt: str) -> Optional[Dict[str, str]]:
        p = prompt.strip()
        low = p.lower()

        if any(k in low for k in ["stato cervello", "stato second brain", "stato obsidian", "quante note ho"]):
            return {"action": "status", "payload": ""}

        daily_prefixes = ("aggiungi al diario:", "aggiungi al diario ", "diario:", "oggi ho ")
        for pref in daily_prefixes:
            if low.startswith(pref):
                text = p[len(pref):].strip() if pref != "oggi ho " else p
                if text:
                    return {"action": "daily", "payload": text}

        capture_prefixes = (
            "salva nel cervello:",
            "salva nel cervello ",
            "ricorda che ",
            "ricorda:",
            "appunta nel cervello:",
            "appunta che ",
            "memorizza:",
        )
        for pref in capture_prefixes:
            if low.startswith(pref):
                text = p[len(pref):].strip()
                if text:
                    return {"action": "capture", "payload": text}

        return None

    def execute_brain_action(self, action_info: Dict[str, str]) -> str:
        if not self.store:
            return "Il Secondo Cervello Obsidian non è al momento raggiungibile."

        act = action_info.get("action")
        payload = action_info.get("payload", "").strip()

        if act == "status":
            s = self.get_stats()
            if not s.get("available"):
                return "Secondo Cervello non disponibile."
            return (
                f"Secondo Cervello attivo: {s['total_notes']} note indicizzate, "
                f"{s['total_links']} collegamenti nel grafo, {s['orphans']} orfani, "
                f"{s['pending_approval']} bozze in attesa di approvazione."
            )
        if act == "daily":
            saved = self.store.log_daily(payload, category="fatto")
            return f"Ho aggiornato il tuo Diario di oggi nel Secondo Cervello ({saved})."
        if act == "capture":
            title = payload[:55].strip()
            saved = self.store.capture_to_inbox(title, payload, tags=["inbox", "mamba-capture"])
            return f"Salvato nel tuo Secondo Cervello ({saved})."

        return "Azione cervello non riconosciuta."

    def sync_compaction_to_vault(self, summary_text: str) -> Optional[str]:
        if not self.store or not summary_text.strip():
            return None
        try:
            return self.store.capture_to_inbox(
                "Compattazione Mamba Token Guard",
                summary_text,
                tags=["mamba-os", "auto-compact", "pending-approval"],
                subfolder="Pending_Approval",
            )
        except Exception:
            return None
