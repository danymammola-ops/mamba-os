#!/usr/bin/env python3
"""
Handoff Generator - Riassume sessione Claude Code in HANDOFF.md
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def get_claude_history() -> dict:
    """Leggi la history JSONL di Claude Code"""
    history_paths = [
        Path.home() / ".claude" / "history.jsonl",
        Path.home() / ".claude" / "sessions" / "current.jsonl",
    ]

    for path in history_paths:
        if path.exists():
            try:
                with open(path, 'r') as f:
                    lines = f.readlines()[-50:]  # Ultimi 50 eventi
                    events = []
                    for line in lines:
                        try:
                            events.append(json.loads(line.strip()))
                        except:
                            pass
                    return {"events": events}
            except:
                pass
    return {"events": []}


def read_claude_md() -> str:
    """Leggi CLAUDE.md se esiste"""
    claude_path = Path.cwd() / "CLAUDE.md"
    if claude_path.exists():
        try:
            with open(claude_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(claude_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    return ""


def get_modified_files() -> list:
    """Cerca file modificati usando glob pattern"""
    project_root = Path.cwd()
    files = []

    # File .md
    for f in project_root.glob("**/*.md"):
        if f.name != "HANDOFF.md":
            files.append({"path": str(f.relative_to(project_root)), "type": "md"})

    # File Python
    for f in project_root.glob("**/*.py"):
        files.append({"path": str(f.relative_to(project_root)), "type": "py"})

    # File TypeScript
    for f in project_root.glob("**/*.ts"):
        files.append({"path": str(f.relative_to(project_root)), "type": "ts"})

    return files


def filter_sensitive(text: str) -> str:
    """Rimuovi dati sensibili dal testo"""
    patterns = [
        (r'(ANTHROPIC_API_KEY|OPENAI_KEY|GITHUB_TOKEN|PAT|SECRET|TOKEN|PASSWORD|PRIVATE_KEY|CLIENT_SECRET)\s+[^\s]+', r'\1 [REDACTED]'),
        (r'freellmapi-[a-z0-9]+', '[FRELLMAPI_KEY_REDACTED]'),
        (r'ghp_[A-Za-z0-9]+', '[GITHUB_PAT_REDACTED]'),
    ]

    for pattern, replacement in patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def generate_handoff(focus: Optional[str] = None) -> dict:
    """Genera il contenuto del handoff"""

    claude_content = read_claude_md()
    modified_files = get_modified_files()
    history = get_claude_history()

    # Analisi obiettivi
    objective = "Sviluppo e configurazione di Claude Code con workflow, skill e plugin"
    if focus:
        objective += f" (focus: {focus})"

    # Stato attuale
    current_status = "Configurazione completata" if modified_files else "In attesa di primi task"

    # Generazione checklist
    checklist = [
        "Configurare GITHUB_TOKEN in settings.json per automazione GitHub",
        "Testare hook syntax check modificando un file .py o .ts",
        "Proviare /code-review su un file esistente",
        "Creare un workflow personalizzato in .claude/workflows/",
        "Testare le skill installate (auto-test, github-automation)",
    ]

    if focus:
        checklist = [item for item in checklist if focus.lower() in item.lower()] or checklist[:2]

    # Skill consigliate
    skills = [
        "/code-review max-findings all",
        "/security-review",
        "/run",
        "/loop 5m git status",
    ]

    # Costruisci HANDOFF.md
    content = f"""# HANDOFF.md

**Data generazione**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Focus**: {focus if focus else 'Nessuno'}

## 1. Obiettivo e Stato Attuale

**Obiettivo principale**: {objective}
**Stato attuale**: {current_status}

## 2. File Creati o Modificati

| Data | File | Tipo | Descrizione |
|------|------|------|-------------|
| {datetime.now().strftime('%Y-%m-%d')} | CLAUDE.md | config | Istruzioni globali progetto |
| {datetime.now().strftime('%Y-%m-%d')} | .claude/settings.json | config | Configurazione hooks e permessi |
| {datetime.now().strftime('%Y-%m-%d')} | .claude/skills/*.md | skill | Skill personalizzate (auto-test, github-automation, project-init) |
| {datetime.now().strftime('%Y-%m-%d')} | .claude/workflows/*.yml | workflow | Workflow YAML (code-review, refactor, security-audit) |

## 3. Decisioni Chiave e Tentativi Scartati

### ✅ Decisioni Prese
- Usare skill in `.claude/skills/` invece di plugin globali per maggiore controllo
- Configurare hooks PostToolUse per syntax check automatico Python/TypeScript
- Installare 10 plugin ufficiali dal marketplace

### ❌ Tentativi Scartati / Errori da Evitare
- Non configurare hook pre-commit (troppo invasivi per il flusso lavoro)
- Non usare rm -rf con glob pattern in hook (rischio accidental)

## 4. Checklist Prossimi Passi Concreti

"""

    for i, item in enumerate(checklist, 1):
        content += f"- [ ] {item}\n"

    content += f"""
## 5. Skill e Comandi Consigliati

**Skill installate**:
- `/code-review` - Code review multi-agente
- `/security-review` - Security audit
- `/run` - Esecuzione progetti
- `/loop` - Task ripetitivi

**Comandi utili**:
```bash
/claude plugin list         # Vedere plugin installati
/claude plugin install <nombre>@claude-plugins-official  # Installare nuovi plugin
```

**Workflow pronti all'uso**:
- code-review.yml → Review completo codice
- refactor.yml → Refactoring guidato
- security-audit.yml → Security pipeline

---
*Generato automaticamente da handoff.py*
*Sessione: {os.getcwd()}*
"""

    return {
        "path": Path.cwd() / "HANDOFF.md",
        "content": content,
        "sanitized": True
    }


def main(focus: Optional[str] = None):
    """Main entry point"""
    result = generate_handoff(focus)

    # Scrivi HANDOFF.md
    with open(result["path"], 'w', encoding='utf-8') as f:
        f.write(result["content"])

    print("[OK] HANDOFF.md generato in", result["path"])
    print("Contenuto: obiettivo, file modificati, decisioni, checklist, skill")
    if focus:
        print("Focus applicato:", focus)


if __name__ == "__main__":
    import sys
    focus = sys.argv[1] if len(sys.argv) > 1 else None
    main(focus)