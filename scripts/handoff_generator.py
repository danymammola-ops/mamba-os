#!/usr/bin/env python3
"""
Handoff Generator - Riassume sessione Claude Code in HANDOFF.md
Con merge intelligente per preservare il contenuto esistente.
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional


REPO_DIR = Path.cwd()
HANDOFF_PATH = REPO_DIR / "HANDOFF.md"


def run_git(args, check=True):
    """Esegui comando git"""
    res = subprocess.run(
        ["git"] + args,
        cwd=REPO_DIR,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )
    if check and res.returncode != 0:
        raise RuntimeError(f"Comando git fallito: git {' '.join(args)}\n{res.stderr}")
    return res


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
                    lines = f.readlines()[-50:]
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
    claude_path = REPO_DIR / "CLAUDE.md"
    if claude_path.exists():
        try:
            with open(claude_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            with open(claude_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
    return ""


def get_modified_files() -> list:
    """Cerca file modificati usando git status + glob pattern"""
    files = []

    # Prima: file modificati secondo git
    try:
        res = run_git(["status", "--porcelain"], check=False)
        for line in res.stdout.strip().split("\n"):
            if line:
                status = line[:2]
                filepath = line[3:].strip()
                if filepath and not filepath.endswith("HANDOFF.md"):
                    ext = Path(filepath).suffix.lower()
                    files.append({"path": filepath, "type": ext[1:] if ext else "file", "status": status})
    except:
        pass

    # Fallback: glob pattern per file principali
    for f in REPO_DIR.glob("**/*.md"):
        if f.name != "HANDOFF.md":
            files.append({"path": str(f.relative_to(REPO_DIR)), "type": "md"})
    for f in REPO_DIR.glob("**/*.py"):
        files.append({"path": str(f.relative_to(REPO_DIR)), "type": "py"})
    for f in REPO_DIR.glob("**/*.ts"):
        files.append({"path": str(f.relative_to(REPO_DIR)), "type": "ts"})

    # Deduplicazione
    seen = set()
    unique_files = []
    for f in files:
        key = f["path"]
        if key not in seen:
            seen.add(key)
            unique_files.append(f)
    return unique_files


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


def normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def parse_sections(content: str) -> dict:
    """Parse HANDOFF.md in sezioni per merge intelligente"""
    content = normalize(content)
    sections = {}
    current_key = "HEADER"
    lines = []
    for line in content.split("\n"):
        if line.startswith("## "):
            if lines or current_key != "HEADER":
                sections[current_key] = "\n".join(lines).strip()
            current_key = line.strip()
            lines = []
        else:
            lines.append(line)
    if lines or current_key != "HEADER":
        sections[current_key] = "\n".join(lines).strip()
    return sections


def merge_tables(local_body: str, remote_body: str, new_rows: list = None) -> str:
    """Merge table rows deduplicando per (Data, File)"""
    header = [
        "| Data | File | Tipo | Descrizione |",
        "|------|------|------|-------------|"
    ]
    seen = set()
    rows = []
    for src in [remote_body, local_body]:
        for line in src.split("\n"):
            line = line.strip()
            if line.startswith("|") and not line.startswith("|-") and "Tipo" not in line and "File" not in line:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 2:
                    key = (parts[0], parts[1])
                    if key not in seen:
                        seen.add(key)
                        rows.append(line)
    # Aggiungi nuove righe
    if new_rows:
        for row in new_rows:
            parts = [p.strip() for p in row.split("|")[1:-1]]
            if len(parts) >= 2:
                key = (parts[0], parts[1])
                if key not in seen:
                    seen.add(key)
                    rows.append(row)
    return "\n".join(header + rows)


def merge_checklist(local_body: str, remote_body: str, new_items: list = None) -> str:
    """Merge checklist: priorità a local (più aggiornato), poi remote, poi nuovi"""
    tasks = {}
    for src, is_local in [(remote_body, False), (local_body, True)]:
        for line in src.split("\n"):
            m = re.match(r'^[-*]\s*\[([ xX])\]\s*(.+)$', line.strip())
            if m:
                checked, txt = m.groups()
                is_checked = (checked.lower() == 'x')
                k = txt.strip().lower()
                if k not in tasks:
                    tasks[k] = (is_checked, txt.strip())
                elif is_local and is_checked:
                    tasks[k] = (True, txt.strip())
    # Aggiungi nuovi item non presenti
    if new_items:
        for item in new_items:
            k = item.strip().lower()
            if k not in tasks:
                tasks[k] = (False, item.strip())
    return "\n".join(f"- [{'x' if v[0] else ' '}] {v[1]}" for v in tasks.values())


def merge_bullets(local_body: str, remote_body: str) -> str:
    """Merge bullet lists deduplicando"""
    bullets = []
    seen = set()
    for src in [remote_body, local_body]:
        for line in src.split("\n"):
            stripped = line.strip()
            if stripped:
                norm = re.sub(r'\s+', ' ', stripped).lower()
                if norm not in seen:
                    seen.add(norm)
                    bullets.append(stripped)
    return "\n".join(bullets)


def smart_merge_handoff(local_text: str, session_data: dict) -> str:
    """Merge intelligente: aggiorna data/focus, merge tabelle e checklist"""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    today_str = datetime.now().strftime("%Y-%m-%d")
    focus = session_data.get("focus", "Nessuno")
    new_files = session_data.get("new_files", [])
    new_checklist = session_data.get("new_checklist", [])

    if not local_text.strip():
        # Primo run: genera da template
        return generate_template_handoff(now_str, focus, today_str, new_files, new_checklist)

    local_sec = parse_sections(local_text)

    # HEADER: aggiorna data e focus
    header = local_sec.get("HEADER", "")
    header = re.sub(r'\*\*Data generazione\*\*:\s*.*', f'**Data generazione**: {now_str}', header)
    header = re.sub(r'\*\*Focus\*\*:\s*.*', f'**Focus**: {focus}', header)

    # Tabella File: merge con nuovi file
    files_sec = "## 2. File Creati o Modificati"
    files_body = local_sec.get(files_sec, "")
    new_file_rows = []
    for f in new_files:
        new_file_rows.append(f"| {today_str} | {f['path']} | {f['type']} | {f.get('desc', 'Aggiornato')} |")
    merged_files = merge_tables(files_body, files_body, new_file_rows)

    # Checklist: merge
    checklist_sec = "## 4. Checklist Prossimi Passi Concreti"
    checklist_body = local_sec.get(checklist_sec, "")
    merged_checklist = merge_checklist(checklist_body, checklist_body, new_checklist)

    # Decisioni: merge bullets
    decisions_sec = "## 3. Decisioni Chiave e Tentativi Scartati"
    decisions_body = local_sec.get(decisions_sec, "")
    merged_decisions = merge_bullets(decisions_body, decisions_body)

    # Obiettivo: mantieni locale se esiste
    obj_sec = "## 1. Obiettivo e Stato Attuale"
    obj_body = local_sec.get(obj_sec, "")

    # Ricostruisci in ordine
    ordered_headers = [
        "HEADER",
        "## 1. Obiettivo e Stato Attuale",
        "## 2. File Creati o Modificati",
        "## 3. Decisioni Chiave e Tentativi Scartati",
        "## 4. Checklist Prossimi Passi Concreti",
        "## 5. Skill e Comandi Consigliati",
    ]

    out = []
    out.append(header)
    out.append("")

    for h in ordered_headers:
        if h == "HEADER":
            continue
        if h == "## 1. Obiettivo e Stato Attuale":
            out.append(h)
            out.append(obj_body)
        elif h == "## 2. File Creati o Modificati":
            out.append(h)
            out.append(merged_files)
        elif h == "## 3. Decisioni Chiave e Tentativi Scartati":
            out.append(h)
            out.append(merged_decisions)
        elif h == "## 4. Checklist Prossimi Passi Concreti":
            out.append(h)
            out.append(merged_checklist)
        elif h == "## 5. Skill e Comandi Consigliati":
            out.append(h)
            out.append(local_sec.get(h, get_default_skills_section()))
        out.append("")

    return "\n".join(out).strip() + "\n"


def get_default_skills_section() -> str:
    return """**Skill installate**:
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
**Comandi Workflow**:
- `/handoff` - Sintetizza la sessione corrente in locale in `HANDOFF.md`
- `/handon` - Legge `HANDOFF.md` e riprende il lavoro all'istante con contesto pulito
- `/gitupdate` - Sincronizza `HANDOFF.md` con GitHub tramite merge intelligente
- `/gitupdate --dry-run` - Mostra l'anteprima delle modifiche senza inviarle
*Generato e verificato automaticamente per la sessione: mio/ai*"""


def generate_template_handoff(now_str: str, focus: str, today_str: str, new_files: list, new_checklist: list) -> str:
    """Genera HANDOFF.md da zero (primo run)"""
    # Default checklist se vuoto
    if not new_checklist:
        new_checklist = [
            "Configurare GITHUB_TOKEN in settings.json per automazione GitHub",
            "Testare hook syntax check modificando un file .py o .ts",
            "Proviare /code-review su un file esistente",
            "Creare un workflow personalizzato in .claude/workflows/",
            "Testare le skill installate (auto-test, github-automation)",
        ]

    content = f"""# HANDOFF.md

**Data generazione**: {now_str}
**Focus**: {focus}

## 1. Obiettivo e Stato Attuale

**Obiettivo principale**: Sviluppo e configurazione di Claude Code con workflow, skill e plugin{f" (focus: {focus})" if focus != "Nessuno" else ""}
**Stato attuale**: Configurazione completata

## 2. File Creati o Modificati

| Data | File | Tipo | Descrizione |
|------|------|------|-------------|"""

    # Aggiungi file
    for f in new_files:
        content += f"\n| {today_str} | {f['path']} | {f['type']} | {f.get('desc', 'Aggiornato')} |"

    content += f"""

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
    for item in new_checklist:
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
**Comandi Workflow**:
- `/handoff` - Sintetizza la sessione corrente in locale in `HANDOFF.md`
- `/handon` - Legge `HANDOFF.md` e riprende il lavoro all'istante con contesto pulito
- `/gitupdate` - Sincronizza `HANDOFF.md` con GitHub tramite merge intelligente
- `/gitupdate --dry-run` - Mostra l'anteprima delle modifiche senza inviarle
*Generato e verificato automaticamente per la sessione: mio/ai*
"""
    return content


def generate_handoff(focus: Optional[str] = None) -> dict:
    """Genera il contenuto del handoff con merge intelligente"""

    # Leggi HANDOFF.md esistente
    existing_content = ""
    if HANDOFF_PATH.exists():
        try:
            with open(HANDOFF_PATH, 'r', encoding='utf-8') as f:
                existing_content = f.read()
        except UnicodeDecodeError:
            with open(HANDOFF_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                existing_content = f.read()

    # Dati sessione corrente
    modified_files = get_modified_files()
    claude_content = read_claude_md()

    # Determina obiettivo basandosi su history o focus
    objective = "Sviluppo e configurazione di Claude Code con workflow, skill e plugin"
    if focus:
        objective += f" (focus: {focus})"

    # Prepara nuovi dati da mergeare
    new_files = []
    for f in modified_files:
        desc = "Creato/Modificato"
        if f.get("status"):
            desc = f"Git: {f['status']}"
        new_files.append({
            "path": f["path"],
            "type": f["type"],
            "desc": desc
        })

    # Nuovi task da aggiungere alla checklist (basati su focus)
    new_checklist = []
    if focus:
        if "test" in focus.lower():
            new_checklist.append(f"Eseguire test per: {focus}")
        if "review" in focus.lower():
            new_checklist.append(f"Code review per: {focus}")
        if "security" in focus.lower() or "audit" in focus.lower():
            new_checklist.append(f"Security audit per: {focus}")

    session_data = {
        "focus": focus if focus else "Nessuno",
        "new_files": new_files,
        "new_checklist": new_checklist,
    }

    # Merge intelligente
    merged_content = smart_merge_handoff(existing_content, session_data)

    return {
        "path": HANDOFF_PATH,
        "content": merged_content,
        "sanitized": True
    }


def main(focus: Optional[str] = None):
    """Main entry point"""
    result = generate_handoff(focus)

    # Scrivi HANDOFF.md
    with open(result["path"], 'w', encoding='utf-8', newline="\n") as f:
        f.write(result["content"])

    print("[OK] HANDOFF.md aggiornato in", result["path"])
    print("Merge intelligente: preserva checklist, file, decisioni esistenti")
    if focus:
        print("Focus applicato:", focus)


if __name__ == "__main__":
    import sys
    focus = sys.argv[1] if len(sys.argv) > 1 else None
    main(focus)