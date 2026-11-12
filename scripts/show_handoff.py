#!/usr/bin/env python3
"""
Handoff Viewer - Mostra il contenuto di HANDOFF.md in modo ordinato
"""
import os
import sys
from pathlib import Path

def read_handoff():
    """Legge e mostra il contenuto di HANDOFF.md"""
    # Cerca HANDOFF.md nella root del progetto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    handoff_file = project_root / "HANDOFF.md"

    if not handoff_file.exists():
        print(f"❌ File HANDOFF.md non trovato in: {project_root}")
        print("Esegui prima '/handoff' per generarlo")
        sys.exit(1)

    with open(handoff_file, 'r', encoding='utf-8') as f:
        content = f.read()

    print("=" * 60)
    print("📋 HANDOFF - Sessione Riepilogo")
    print("=" * 60)
    print()
    print(content)

if __name__ == "__main__":
    read_handoff()