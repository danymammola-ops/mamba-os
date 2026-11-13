#!/usr/bin/env python3
"""
gitupdate.py - Sincronizzazione intelligente di HANDOFF.md con GitHub.
Esegue il merge senza duplicati e sincronizza su GitHub tramite Git nativo.
"""

import os
import sys
import re
import subprocess
from datetime import datetime

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HANDOFF_PATH = os.path.join(REPO_DIR, "HANDOFF.md")

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

def main():
    dry_run = "--dry-run" in sys.argv
    diff_mode = "--diff" in sys.argv

    print("🔄 [gitupdate] Sincronizzazione intelligente HANDOFF.md con GitHub...")

    if not os.path.exists(HANDOFF_PATH):
        print(f"❌ [gitupdate] File {HANDOFF_PATH} non trovato!")
        sys.exit(1)

    with open(HANDOFF_PATH, "r", encoding="utf-8") as f:
        local_content = f.read()

    # Fetch remote
    try:
        run_git(["fetch", "origin", "main"], check=False)
    except Exception:
        pass

    remote_res = run_git(["show", "origin/main:HANDOFF.md"], check=False)
    remote_content = remote_res.stdout if remote_res.returncode == 0 else ""

    merged = smart_merge(local_content, remote_content)

    if dry_run or diff_mode:
        print("🔍 [gitupdate] DRY-RUN / DIFF anteprima:")
        print(merged[:500] + "\n... (anteprima completata)")
        print("✅ [gitupdate] Dry-run terminato con successo.")
        return 0

    # Write merged content
    with open(HANDOFF_PATH, "w", encoding="utf-8", newline="\n") as f:
        f.write(merged)

    # Git commit and push
    try:
        run_git(["add", "HANDOFF.md"])
        status = run_git(["status", "--porcelain", "HANDOFF.md"]).stdout.strip()
        if status:
            msg = f"chore: smart sync HANDOFF.md ({datetime.now().strftime('%Y-%m-%d %H:%M')})"
            run_git(["commit", "-m", msg])
            print(f"📝 [gitupdate] Commit creato: {msg}")

        # Pull rebase before push to avoid divergence
        run_git(["pull", "--rebase", "origin", "main"], check=False)
        push_res = run_git(["push", "origin", "main"])
        print("✅ [gitupdate] Sincronizzazione con GitHub completata con successo!")
        print(push_res.stdout.strip() or "All changes pushed to origin/main.")
    except Exception as e:
        print(f"⚠️ [gitupdate] Nota sul push: {e}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
