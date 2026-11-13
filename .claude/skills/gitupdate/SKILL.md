---
name: gitupdate
description: Sincronizza intelligentemente HANDOFF.md con GitHub fondendo modifiche, checklist e tabelle senza duplicazioni.
argument-hint: "[--dry-run|--diff]"
disable-model-invocation: true
allowed-tools: Read, Write, Grep, Glob, Bash
---

# GitUpdate

Sincronizza in modo intelligente il file locale `HANDOFF.md` col repository GitHub remoto.

Esegue lo script di sincronizzazione:
```bash
python scripts/gitupdate.py $ARGUMENTS
```
