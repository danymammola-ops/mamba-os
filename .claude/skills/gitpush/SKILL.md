---
name: gitpush
description: Backup completo del progetto su GitHub e smart sync di HANDOFF.md senza duplicazioni.
argument-hint: "[--dry-run|--diff]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash
---

# GitPush & Project Backup

Esegue il backup completo di tutto il progetto su GitHub e sincronizza in modo intelligente `HANDOFF.md` fondendo tabelle, checklist e decisioni senza duplicati.

Esegue:
```bash
python scripts/gitpush.py $ARGUMENTS
```
