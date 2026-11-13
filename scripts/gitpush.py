#!/usr/bin/env python3
"""
gitpush.py - Backup completo del progetto e sincronizzazione intelligente di HANDOFF.md e README.md con GitHub.
Esegue:
1. Rileva automaticamente tutti i file nuovi/modificati dal git status (anche se l'utente non ha eseguito /handoff).
2. Smart merge di HANDOFF.md (preservando tabelle, checklist e decisioni remote e locali senza duplicati).
3. Inietta i file rilevati in HANDOFF.md e aggiorna la guida scritta del progetto (README.md) con stato, checklist e file.
4. Backup totale di tutti i file di progetto creati/modificati/eliminati su GitHub (git add -A).
5. Commit e push su origin <branch> per avere un ripristino istantaneo via git pull.
Funziona globalmente su qualsiasi cartella di lavoro (repository git).
"""

import os
import sys
import re
import subprocess
from datetime import datetime

REPO_DIR = os.getcwd()
HANDOFF_PATH = os.path.join(REPO_DIR, "HANDOFF.md")
if not os.path.exists(HANDOFF_PATH):
    temp_path = os.path.join(os.environ.get("TEMP", ""), "HANDOFF.md")
    if os.path.exists(temp_path):
        HANDOFF_PATH = temp_path

README_PATH = os.path.join(REPO_DIR, "README.md")

def run_git(args, check=True):
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

def get_current_branch():
    res = run_git(["branch", "--show-current"], check=False)
    branch = res.stdout.strip() if res.returncode == 0 else ""
    return branch or "main"

def is_git_repo():
    res = run_git(["rev-parse", "--is-inside-work-tree"], check=False)
    return res.returncode == 0 and res.stdout.strip() == "true"

def normalize(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")

def parse_sections(content):
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

def merge_tables(local_body, remote_body):
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
    return "\n".join(header + rows)

def merge_checklist(local_body, remote_body):
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
    return "\n".join(f"- [{'x' if v[0] else ' '}] {v[1]}" for v in tasks.values())

def merge_bullets(local_body, remote_body):
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

def smart_merge(local_text, remote_text):
    if not remote_text.strip():
        return normalize(local_text)
    if not local_text.strip():
        return normalize(remote_text)

    local_sec = parse_sections(local_text)
    remote_sec = parse_sections(remote_text)

    merged = {}
    all_headers = []
    for h in list(local_sec.keys()) + list(remote_sec.keys()):
        if h not in all_headers:
            all_headers.append(h)

    for h in all_headers:
        lb = local_sec.get(h, "")
        rb = remote_sec.get(h, "")

        if h == "HEADER":
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            hdr = re.sub(r'\*\*Data generazione\*\*:\s*.*', f'**Data generazione**: {now_str}', lb)
            merged[h] = hdr
        elif "File Creati" in h:
            merged[h] = merge_tables(lb, rb)
        elif "Checklist" in h:
            merged[h] = merge_checklist(lb, rb)
        elif "Decisioni" in h:
            merged[h] = merge_bullets(lb, rb)
        elif "Obiettivo" in h:
            merged[h] = lb if lb else rb
        else:
            merged[h] = merge_bullets(lb, rb)

    out = []
    if "HEADER" in merged:
        out.append(merged["HEADER"])
        out.append("")

    for h in all_headers:
        if h == "HEADER":
            continue
        out.append(h)
        out.append(merged.get(h, ""))
        out.append("")

    return "\n".join(out).strip() + "\n"

def get_git_detected_changes(repo_dir):
    """Rileva file modificati, creati o eliminati direttamente dal working tree di git."""
    res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
    today = datetime.now().strftime("%Y-%m-%d")
    changes = []
    desc_map = {"M": "Modificato", "A": "Nuovo file", "??": "Nuovo file", "D": "Eliminato", "R": "Rinominato"}
    for line in res.stdout.split("\n"):
        line = line.strip()
        if not line:
            continue
        status = line[:2].strip()
        filepath = line[2:].strip().replace('"', "")
        if filepath in ("HANDOFF.md", "README.md"):
            continue
        desc = desc_map.get(status, "Aggiornato")
        ext = filepath.split(".")[-1] if "." in filepath else "file"
        changes.append({
            "date": today,
            "path": filepath,
            "type": ext,
            "desc": desc
        })
    return changes

def sync_git_changes_into_handoff(handoff_path, git_changes):
    """Inietta i file modificati rilevati da git dentro HANDOFF.md se non presenti."""
    if not git_changes:
        return

    content = ""
    if os.path.exists(handoff_path):
        with open(handoff_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        content = f"""# HANDOFF.md

**Data generazione**: {now_str}
**Focus**: Sincronizzazione automatica gitpush

## 1. Obiettivo e Stato Attuale
**Obiettivo principale**: Sviluppo e gestione progetto con backup automatico GitHub.
**Stato attuale**: Sincronizzato con GitHub.

## 2. File Creati o Modificati
| Data | File | Tipo | Descrizione |
|------|------|------|-------------|

## 3. Decisioni Chiave e Tentativi Scartati
- Sincronizzazione automatica gitpush attiva

## 4. Checklist Prossimi Passi Concreti
- [x] Sincronizzazione repository e backup GitHub
"""

    table_pattern = r"(## 2\.\s*File Creati o Modificati[\s\S]*?)(\n##|\Z)"
    match = re.search(table_pattern, content)
    if match:
        table_block = match.group(1)
        suffix = match.group(2)

        existing_paths = set()
        for line in table_block.split("\n"):
            line = line.strip()
            if line.startswith("|") and not line.startswith("|-") and "Tipo" not in line and "File" not in line:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 2:
                    existing_paths.add(parts[1])

        new_rows = []
        for c in git_changes:
            if c["path"] not in existing_paths:
                new_rows.append(f"| {c['date']} | {c['path']} | {c['type']} | {c['desc']} |")
                existing_paths.add(c["path"])

        if new_rows:
            updated_table = table_block.rstrip() + "\n" + "\n".join(new_rows) + "\n"
            content = content[:match.start(1)] + updated_table + suffix + content[match.end():]

    with open(handoff_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)

def update_readme_from_handoff(repo_dir, handoff_path):
    readme_path = os.path.join(repo_dir, "README.md")
    if not os.path.exists(readme_path) or not os.path.exists(handoff_path):
        return False

    try:
        with open(handoff_path, "r", encoding="utf-8") as f:
            handoff_text = f.read()

        with open(readme_path, "r", encoding="utf-8") as f:
            readme_text = f.read()

        # Estrai Data di generazione
        date_m = re.search(r"\*\*Data generazione\*\*:\s*(.+)", handoff_text)
        date_str = date_m.group(1).strip() if date_m else datetime.now().strftime("%Y-%m-%d %H:%M")

        # Estrai Obiettivo e Stato Attuale
        obj_m = re.search(r"\*\*Obiettivo principale\*\*:\s*(.+)", handoff_text)
        obj_str = obj_m.group(1).strip() if obj_m else ""

        stat_m = re.search(r"\*\*Stato attuale\*\*:\s*(.+)", handoff_text)
        stat_str = stat_m.group(1).strip() if stat_m else ""

        # Estrai Checklist (senza duplicazioni)
        checklist = []
        seen = set()
        for line in handoff_text.split("\n"):
            m = re.match(r"^\s*[-*]\s*\[([ xX])\]\s*(.+)$", line)
            if m:
                c, t = m.groups()
                txt = t.strip()
                k = txt.lower()
                if k not in seen:
                    seen.add(k)
                    checklist.append(f"- [{c}] {txt}")

        checklist_str = "\n".join(checklist) if checklist else "- [x] Nessun task pendente"

        # Estrai ultimi file modificati per dare visibilità immediata su GitHub
        table_files = []
        seen_paths = set()
        for line in handoff_text.split("\n"):
            line = line.strip()
            if line.startswith("|") and not line.startswith("|-") and "Tipo" not in line and "File" not in line:
                parts = [p.strip() for p in line.split("|")[1:-1]]
                if len(parts) >= 4:
                    if parts[1] not in seen_paths:
                        seen_paths.add(parts[1])
                        table_files.append(line)

        recent_files_block = ""
        if table_files:
            recent_files_block = "### 📁 Ultimi File Modificati / Rilevati nel Progetto:\n| Data | File | Tipo | Descrizione |\n|------|------|------|-------------|\n" + "\n".join(table_files[-6:]) + "\n\n"

        new_guide_section = f"""## 📄 Workflow di Sessione & Backup

Questo progetto utilizza il ciclo di sessione a 3 comandi per azzerare il consumo di token e mantenere la repository GitHub come **copia di backup identica del progetto locale**:

| Comando | Descrizione | Ambito |
|---------|-------------|--------|
| `/handoff [focus]` | Salva e sintetizza la sessione corrente in locale in `HANDOFF.md` | **100% Locale** (zero chiamate di rete) |
| `/handon [sezione]` | Legge `HANDOFF.md` e riprende il lavoro all'istante con contesto pulito | **100% Locale** |
| `/gitpush` | Rileva modifiche, aggiorna `README.md` e carica tutto su GitHub | **Remoto** (Backup Completo) |
| `/gitpush --dry-run` | Mostra l'anteprima dei file e delle modifiche senza inviarle | Anteprima |

---

## 📌 Stato del Progetto & Avanzamento (Sincronizzato da HANDOFF.md)

*Ultimo aggiornamento: {date_str}*

**Obiettivo principale**: {obj_str}  
**Stato attuale**: {stat_str}

{recent_files_block}### Checklist Prossimi Passi:
{checklist_str}
"""

        # Aggiorna la sezione Handoff / Workflow nel README usando lambda per evitare escape errati
        pattern = r"(##\s*(?:[^\n]*Handoff|[^\n]*Workflow di Sessione)[\s\S]*)"
        if re.search(pattern, readme_text):
            updated_readme = re.sub(pattern, lambda m: new_guide_section, readme_text)
        else:
            updated_readme = readme_text.strip() + "\n\n" + new_guide_section

        # Aggiorna anche la tabella dei comandi principali se presente
        if "| `/handoff`" in updated_readme and "/gitpush" not in updated_readme.split("## 🛠️ Comandi Principali")[1].split("##")[0]:
            updated_table = (
                "| `/handoff` | Salva la sessione in locale in HANDOFF.md |\n"
                "| `/handon` | Legge HANDOFF.md e riprende il lavoro con contesto pulito |\n"
                "| `/gitpush` | Rileva modifiche, aggiorna README.md ed esegue il backup su GitHub |\n"
            )
            updated_readme = re.sub(r"\| `/handoff`[^\n]*\n", lambda m: updated_table, updated_readme)

        with open(readme_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(updated_readme)

        return True
    except Exception as e:
        print(f"⚠️ [gitpush] Avviso durante aggiornamento README.md: {e}")
        return False

def main():
    dry_run = "--dry-run" in sys.argv
    diff_mode = "--diff" in sys.argv

    print(f"🔄 [gitpush] Avvio sincronizzazione & backup completo su GitHub ({REPO_DIR})...")

    if not is_git_repo():
        print(f"❌ [gitpush] La directory {REPO_DIR} non è un repository Git!")
        sys.exit(1)

    branch = get_current_branch()

    # 1. Fetch remote branch
    try:
        run_git(["fetch", "origin", branch], check=False)
    except Exception:
        pass

    # 2. Rileva modifiche vive nel progetto da Git (anche senza aver fatto /handoff)
    git_changes = get_git_detected_changes(REPO_DIR)
    if git_changes:
        print(f"🔍 [gitpush] Rilevate {len(git_changes)} modifiche nel progetto via Git status.")
        if not dry_run and not diff_mode:
            sync_git_changes_into_handoff(HANDOFF_PATH, git_changes)

    # 3. Smart merge di HANDOFF.md con il remoto se presente
    merged = ""
    if os.path.exists(HANDOFF_PATH):
        try:
            with open(HANDOFF_PATH, "r", encoding="utf-8") as f:
                local_content = f.read()

            remote_res = run_git(["show", f"origin/{branch}:HANDOFF.md"], check=False)
            remote_content = remote_res.stdout if remote_res.returncode == 0 else ""

            merged = smart_merge(local_content, remote_content)

            if not dry_run and not diff_mode:
                with open(HANDOFF_PATH, "w", encoding="utf-8", newline="\n") as f:
                    f.write(merged)
        except Exception as e:
            print(f"⚠️ [gitpush] Avviso durante smart merge HANDOFF.md: {e}")

    # 4. Aggiorna la guida del progetto (README.md) con dati freschi e modifiche vive
    if not dry_run and not diff_mode:
        if update_readme_from_handoff(REPO_DIR, HANDOFF_PATH):
            print("📖 [gitpush] Guida scritta (README.md) aggiornata con stato, checklist e modifiche vive.")

    # 5. Stage di tutti i file di progetto (rispettando .gitignore)
    if not dry_run and not diff_mode:
        run_git(["add", "-A"])
        status_res = run_git(["status", "--porcelain"])
    else:
        status_res = run_git(["status", "--porcelain"])

    raw_status = status_res.stdout.strip()
    changes = [l.strip() for l in raw_status.split("\n") if l.strip()]

    # Anteprima se dry-run o diff
    if dry_run or diff_mode:
        print(f"🔍 [gitpush] ANTEPRIMA BACKUP (DRY-RUN) - Branch: origin/{branch}:")
        if merged:
            print(f"--- Anteprima HANDOFF.md ({HANDOFF_PATH}) ---")
            print(merged[:350] + "\n... (omesso resto anteprima)")
        if os.path.exists(README_PATH):
            print(f"--- Guida scritta ({README_PATH}) verrebbe aggiornata con modifiche e dati freschi ---")
        print(f"--- File da backuppare su GitHub ({len(changes)} modifiche rilevate) ---")
        if changes:
            for c in changes[:20]:
                print(f"  {c}")
            if len(changes) > 20:
                print(f"  ... e altri {len(changes) - 20} file")
        else:
            print("  (Nessun file modificato)")
        print("✅ [gitpush] Dry-run completato (nessun push effettuato).")
        return 0

    if not changes:
        print(f"ℹ️ [gitpush] Nessun file modificato: il progetto su origin/{branch} è già perfettamente sincronizzato e al sicuro.")
        return 0

    # 6. Creazione commit descrittivo
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    has_handoff = any("HANDOFF.md" in c for c in changes)
    has_readme = any("README.md" in c for c in changes)
    other_files = [c for c in changes if "HANDOFF.md" not in c and "README.md" not in c]

    parts = []
    if other_files:
        parts.append(f"sync project files ({len(other_files)} files)")
    if has_readme:
        parts.append("update README.md")
    if has_handoff:
        parts.append("sync HANDOFF.md")

    commit_msg = f"backup: {', '.join(parts)} ({now_str})"

    run_git(["commit", "-m", commit_msg])
    print(f"📝 [gitpush] Commit di backup creato: {commit_msg}")
    print(f"📦 [gitpush] File inclusi nel backup: {len(changes)}")

    # 7. Rebase e Push su GitHub
    try:
        run_git(["pull", "--rebase", "-X", "ours", "origin", branch], check=False)
        push_res = run_git(["push", "origin", branch])
        print(f"🚀 [gitpush] Backup completo su GitHub (origin/{branch}) completato con successo!")
        print(f"🛡️ [gitpush] Copia esatta online: se serve ripristinare il progetto basta eseguire 'git pull origin {branch}'")
        if push_res.stdout.strip():
            print(push_res.stdout.strip())
    except Exception as e:
        print(f"⚠️ [gitpush] Errore durante il push: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
