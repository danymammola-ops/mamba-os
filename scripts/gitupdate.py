#!/usr/bin/env python3
"""
gitupdate.py - Backup completo del progetto e sincronizzazione intelligente di HANDOFF.md e README.md con GitHub.
Esegue:
1. Smart merge di HANDOFF.md (preservando tabelle, checklist e decisioni remote e locali senza duplicati).
2. Aggiornamento automatico della guida del progetto (README.md) estraendo stato, checklist e comandi da HANDOFF.md.
3. Backup totale di tutti i file di progetto creati/modificati/eliminati su GitHub (git add -A).
4. Commit e push su origin <branch> per avere un ripristino istantaneo via git pull.
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

        new_guide_section = f"""## 📄 Workflow di Sessione & Backup

Questo progetto utilizza il ciclo di sessione a 3 comandi per azzerare il consumo di token e mantenere la repository GitHub come **copia di backup identica del progetto locale**:

| Comando | Descrizione | Ambito |
|---------|-------------|--------|
| `/handoff [focus]` | Salva e sintetizza la sessione corrente in locale in `HANDOFF.md` | **100% Locale** (zero chiamate di rete) |
| `/handon [sezione]` | Legge `HANDOFF.md` e riprende il lavoro all'istante con contesto pulito | **100% Locale** |
| `/gitupdate` | Legge `HANDOFF.md`, aggiorna questa guida (`README.md`) e crea un backup completo su GitHub | **Remoto** (Backup Completo) |
| `/gitupdate --dry-run` | Mostra l'anteprima dei file e delle modifiche senza inviarle | Anteprima |

---

## 📌 Stato del Progetto & Avanzamento (Sincronizzato da HANDOFF.md)

*Ultimo aggiornamento: {date_str}*

**Obiettivo principale**: {obj_str}  
**Stato attuale**: {stat_str}

### Checklist Prossimi Passi:
{checklist_str}
"""

        # Aggiorna la sezione Handoff / Workflow nel README
        pattern = r"(##\s*(?:[^\n]*Handoff|[^\n]*Workflow di Sessione)[\s\S]*)"
        if re.search(pattern, readme_text):
            updated_readme = re.sub(pattern, new_guide_section, readme_text)
        else:
            updated_readme = readme_text.strip() + "\n\n" + new_guide_section

        # Aggiorna anche la tabella dei comandi principali se presente
        if "| `/handoff`" in updated_readme and "/gitupdate" not in updated_readme.split("## 🛠️ Comandi Principali")[1].split("##")[0]:
            updated_table = (
                "| `/handoff` | Salva la sessione in locale in HANDOFF.md |\n"
                "| `/handon` | Legge HANDOFF.md e riprende il lavoro con contesto pulito |\n"
                "| `/gitupdate` | Aggiorna README.md ed esegue il backup completo su GitHub |\n"
            )
            updated_readme = re.sub(r"\| `/handoff`[^\n]*\n", updated_table, updated_readme)

        with open(readme_path, "w", encoding="utf-8", newline="\n") as f:
            f.write(updated_readme)

        return True
    except Exception as e:
        print(f"⚠️ [gitupdate] Avviso durante aggiornamento README.md: {e}")
        return False

def main():
    dry_run = "--dry-run" in sys.argv
    diff_mode = "--diff" in sys.argv

    print(f"🔄 [gitupdate] Avvio sincronizzazione & backup completo su GitHub ({REPO_DIR})...")

    if not is_git_repo():
        print(f"❌ [gitupdate] La directory {REPO_DIR} non è un repository Git!")
        sys.exit(1)

    branch = get_current_branch()

    # 1. Fetch remote branch
    try:
        run_git(["fetch", "origin", branch], check=False)
    except Exception:
        pass

    # 2. Smart merge di HANDOFF.md se presente
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
            print(f"⚠️ [gitupdate] Avviso durante smart merge HANDOFF.md: {e}")

    # 3. Aggiorna la guida del progetto (README.md) leggendo HANDOFF.md
    if not dry_run and not diff_mode:
        if update_readme_from_handoff(REPO_DIR, HANDOFF_PATH):
            print("📖 [gitupdate] Guida scritta (README.md) aggiornata con stato e comandi da HANDOFF.md.")

    # 4. Stage di tutti i file di progetto (rispettando .gitignore)
    if not dry_run and not diff_mode:
        run_git(["add", "-A"])
        status_res = run_git(["status", "--porcelain"])
    else:
        status_res = run_git(["status", "--porcelain"])

    raw_status = status_res.stdout.strip()
    changes = [l.strip() for l in raw_status.split("\n") if l.strip()]

    # Anteprima se dry-run o diff
    if dry_run or diff_mode:
        print(f"🔍 [gitupdate] ANTEPRIMA BACKUP (DRY-RUN) - Branch: origin/{branch}:")
        if merged:
            print(f"--- Anteprima HANDOFF.md ({HANDOFF_PATH}) ---")
            print(merged[:350] + "\n... (omesso resto anteprima)")
        if os.path.exists(README_PATH):
            print(f"--- Guida scritta ({README_PATH}) verrebbe aggiornata con i dati di HANDOFF.md ---")
        print(f"--- File da backuppare su GitHub ({len(changes)} modifiche rilevate) ---")
        if changes:
            for c in changes[:20]:
                print(f"  {c}")
            if len(changes) > 20:
                print(f"  ... e altri {len(changes) - 20} file")
        else:
            print("  (Nessun file modificato)")
        print("✅ [gitupdate] Dry-run completato (nessun push effettuato).")
        return 0

    if not changes:
        print(f"ℹ️ [gitupdate] Nessun file modificato: il progetto su origin/{branch} è già perfettamente sincronizzato e al sicuro.")
        return 0

    # 5. Creazione commit descrittivo
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
    print(f"📝 [gitupdate] Commit di backup creato: {commit_msg}")
    print(f"📦 [gitupdate] File inclusi nel backup: {len(changes)}")

    # 6. Rebase e Push su GitHub
    try:
        run_git(["pull", "--rebase", "-X", "ours", "origin", branch], check=False)
        push_res = run_git(["push", "origin", branch])
        print(f"🚀 [gitupdate] Backup completo su GitHub (origin/{branch}) completato con successo!")
        print(f"🛡️ [gitupdate] Copia esatta online: se serve ripristinare il progetto basta eseguire 'git pull origin {branch}'")
        if push_res.stdout.strip():
            print(push_res.stdout.strip())
    except Exception as e:
        print(f"⚠️ [gitupdate] Errore durante il push: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
