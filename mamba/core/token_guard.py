#!/usr/bin/env python3
"""
mamba/core/token_guard.py - Token Guard & Auto-Compaction Engine (Soglia 50.000 tokens)
Garantisce:
- Monitoraggio della memoria di contesto.
- Compattazione automatica quando si supera la soglia di 50k token.
- Sintesi tramite FreeLLMAPI a costo zero.
- Preservazione di preferenze, checklist e decisioni in MAMBA-MEMORIA.md.
"""

import os
import sys
import json
import time
from typing import List, Dict, Any, Tuple, Optional
from freellm_client import FreeLLMClient

DEFAULT_MAX_TOKENS = 50000
CHARS_PER_TOKEN = 4.0  # Stima approssimativa standard

class TokenGuard:
    def __init__(self, max_tokens: int = DEFAULT_MAX_TOKENS, client: Optional[FreeLLMClient] = None):
        self.max_tokens = max_tokens
        self.client = client or FreeLLMClient()
        self.compaction_count = 0
        self.data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
        os.makedirs(self.data_dir, exist_ok=True)
        self.memory_path = os.path.join(self.data_dir, "MAMBA-MEMORIA.md")

    def estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Calcola la stima dei token consumati dalla conversazione."""
        total_chars = sum(len(m.get("content", "")) for m in messages)
        return int(total_chars / CHARS_PER_TOKEN)

    def should_compact(self, messages: List[Dict[str, str]]) -> bool:
        """Verifica se il contesto supera la soglia dei 50k token."""
        return self.estimate_tokens(messages) >= self.max_tokens

    def compact(self, messages: List[Dict[str, str]], keep_recent: int = 4) -> Tuple[List[Dict[str, str]], str]:
        """
        Compatta la cronologia:
        1. Estrae i messaggi storici eccetto gli ultimi `keep_recent`.
        2. Chiama FreeLLMAPI a costo zero per sintetizzare i punti chiave.
        3. Scrive la sintesi in MAMBA-MEMORIA.md.
        4. Restituisce il nuovo array messaggi [System Summary, ...recent].
        """
        if len(messages) <= keep_recent:
            return messages, ""

        historical = messages[:-keep_recent]
        recent = messages[-keep_recent:]

        print(f"🛡️ [Token Guard] Attivazione Auto-Compact a {self.max_tokens} tokens (Messaggi storici: {len(historical)})...")

        prompt_summary = [
            {
                "role": "system",
                "content": (
                    "Sei il modulo di compattazione memoria di Mamba OS. "
                    "Analizza i messaggi storici forniti ed estrai una sintesi ultra-densa in bullet points:\n"
                    "- Fatti e preferenze dell'utente\n"
                    "- Task completati e decisioni prese\n"
                    "- Obiettivo attivo in corso\n"
                    "Sii conciso ed elimina ogni convenevole o ridondanza."
                )
            },
            {
                "role": "user",
                "content": f"Cronologia storica da compattare:\n{json.dumps(historical, ensure_ascii=False)}"
            }
        ]

        try:
            res = self.client.chat(prompt_summary, model="auto:fast", temperature=0.3, timeout=12)
            summary_text = res.get("content", "").strip()
        except Exception as e:
            summary_text = f"Sintesi automatica (fallback): {len(historical)} messaggi storici archiviati per limite token."

        self.compaction_count += 1
        self._append_to_memory(summary_text)

        # Crea il nuovo array compattato
        compacted_messages = [
            {
                "role": "system",
                "content": f"[MEMORIA COMPATTATA MAMBA - Ciclo #{self.compaction_count}]\n{summary_text}"
            }
        ] + recent

        tokens_before = self.estimate_tokens(messages)
        tokens_after = self.estimate_tokens(compacted_messages)
        print(f"✅ [Token Guard] Compattazione completata: {tokens_before} token -> {tokens_after} token (Risparmiati: {tokens_before - tokens_after}).")

        return compacted_messages, summary_text

    def _append_to_memory(self, summary_text: str):
        """Salva la sintesi nel file persistente MAMBA-MEMORIA.md."""
        now_str = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"\n\n### 📦 Auto-Compact #{self.compaction_count} ({now_str})\n{summary_text}\n"
        
        mode = "a" if os.path.exists(self.memory_path) else "w"
        with open(self.memory_path, mode, encoding="utf-8") as f:
            if mode == "w":
                f.write("# 🧠 MAMBA-MEMORIA.md - Memoria Persistente di Mamba OS\n\nMemoria continua auto-compattata dal Token Guard a 50k tokens.\n")
            f.write(entry)

if __name__ == "__main__":
    guard = TokenGuard(max_tokens=100) # Soglia bassa per test
    fake_messages = [
        {"role": "user", "content": "Ciao Mamba, ricordati che sto sviluppando un'applicazione per analizzare il traffico di rete."},
        {"role": "assistant", "content": "Certamente signore, informazione memorizzata."},
        {"role": "user", "content": "Abbiamo anche deciso di usare Python 3.12 e di non toccare i file di configurazione senza autorizzazione."},
        {"role": "assistant", "content": "Decisione archiviata con successo."},
        {"role": "user", "content": "Qual è il prossimo passo adesso?"}
    ]
    
    tokens = guard.estimate_tokens(fake_messages)
    print(f"Token stimati: {tokens} (Soglia test: {guard.max_tokens})")
    if guard.should_compact(fake_messages):
        new_history, summary = guard.compact(fake_messages, keep_recent=2)
        print("\nNuova cronologia compattata:")
        for m in new_history:
            print(f"[{m['role']}]: {m['content'][:70]}...")
