#!/usr/bin/env python3
"""
scripts/checkpoint.py - Sistema di Checkpoint & Rollback per Mamba OS
Permette di salvare uno stato verificato del progetto come Git Tag e ripristinarlo in qualsiasi momento.

Uso:
  python scripts/checkpoint.py create <nome-checkpoint> "descrizione opzionale"
  python scripts/checkpoint.py list
  python scripts/checkpoint.py restore <nome-checkpoint>
"""

import sys
import subprocess
import os
import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHECKPOINTS_FILE = os.path.join(ROOT_DIR, "docs", "CHECKPOINTS.md")

def run_git(*args):
    res = subprocess.run(["git", *args], cwd=ROOT_DIR, capture_output=True, text=True, encoding="utf-8")
    return res.returncode, res.stdout.strip(), res.stderr.strip()

def create_checkpoint(name: str, description: str = ""):
    tag_name = f"checkpoint/{name.lower().replace(' ', '-')}"
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    desc = description or f"Checkpoint: {name}"

    # 1. Stage e commit di eventuali modifiche pendenti
    run_git("add", "-A")
    code, out, _ = run_git("commit", "-m", f"chore(checkpoint): {desc} [{now}]")
    
    # 2. Crea tag annotato
    code, out, err = run_git("tag", "-a", tag_name, "-m", f"{desc} ({now})", "-f")
    if code != 0:
        print(f"❌ Errore creazione tag git: {err}")
        return False

    # 3. Registra nel registro storico dei checkpoint
    os.makedirs(os.path.dirname(CHECKPOINTS_FILE), exist_ok=True)
    entry = f"| `{tag_name}` | {now} | {desc} |\n"
    
    if not os.path.exists(CHECKPOINTS_FILE):
        header = "# 📌 Mamba OS — Registro Checkpoint\n\n| Tag Checkpoint | Data & Ora | Descrizione |\n|---|---|---|\n"
        with open(CHECKPOINTS_FILE, "w", encoding="utf-8") as f:
            f.write(header + entry)
    else:
        with open(CHECKPOINTS_FILE, "a", encoding="utf-8") as f:
            f.write(entry)

    print(f"✅ Checkpoint creato con successo: '{tag_name}'")
    print(f"📝 Registrato in: docs/CHECKPOINTS.md")
    return True

def list_checkpoints():
    code, out, _ = run_git("tag", "-l", "checkpoint/*", "--sort=-creatordate")
    if not out:
        print("Nessun checkpoint trovato.")
        return
    print("\n📌 Checkpoint disponibili per il ripristino:")
    for tag in out.splitlines():
        _, info, _ = run_git("tag", "-n1", tag)
        print(f"  • {tag:<35} -> {info.strip()}")
    print("\nPer ripristinare uno stato: python scripts/checkpoint.py restore <nome-tag>")

def restore_checkpoint(tag_name: str):
    if not tag_name.startswith("checkpoint/"):
        tag_name = f"checkpoint/{tag_name}"
        
    code, out, err = run_git("tag", "-l", tag_name)
    if not out:
        print(f"❌ Checkpoint '{tag_name}' non trovato!")
        list_checkpoints()
        return False

    print(f"⚠️ Ripristino del checkpoint '{tag_name}' in corso...")
    # Crea un ramo di backup prima del ripristino per sicurezza assoluta
    backup_tag = f"backup/before-restore-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    run_git("tag", backup_tag)
    
    # Checkout pulito dello stato
    code, out, err = run_git("checkout", tag_name)
    if code == 0:
        print(f"✅ Progetto ripristinato esattamente al checkpoint '{tag_name}'!")
        print(f"🛡️ Backup dello stato precedente salvato in: '{backup_tag}'")
        return True
    else:
        print(f"❌ Errore durante il checkout: {err}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/checkpoint.py [create|list|restore] [nome]")
        sys.exit(1)

    cmd = sys.argv[1].lower()
    if cmd == "create":
        c_name = sys.argv[2] if len(sys.argv) > 2 else f"step-{datetime.datetime.now().strftime('%Y%m%d%H%M')}"
        c_desc = sys.argv[3] if len(sys.argv) > 3 else ""
        create_checkpoint(c_name, c_desc)
    elif cmd == "list":
        list_checkpoints()
    elif cmd == "restore":
        if len(sys.argv) < 3:
            print("Specifica il nome del checkpoint da ripristinare.")
            list_checkpoints()
            sys.exit(1)
        restore_checkpoint(sys.argv[2])
    else:
        print(f"Comando sconosciuto: {cmd}")
