---
name: gitupdate
description: Sincronizza intelligentemente HANDOFF.md con GitHub senza duplicati
argumentHint: "[--dry-run|--diff]"
---

# Comando: /gitupdate

## Uso
```
/gitupdate                  # Sincronizza intelligentemente HANDOFF.md con GitHub
/gitupdate --dry-run        # Mostra l'anteprima delle differenze senza inviare
```

## Cosa fa
- Legge il file locale `HANDOFF.md` e la versione remota su GitHub
- Fonde tabelle e checklist senza duplicati
- Crea il commit e invia le modifiche a GitHub
