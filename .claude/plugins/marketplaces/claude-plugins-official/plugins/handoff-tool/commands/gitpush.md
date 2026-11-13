---
name: gitpush
description: Sincronizza intelligentemente HANDOFF.md con GitHub ed esegue il backup senza duplicati
argumentHint: "[--dry-run|--diff]"
---

# Comando: /gitpush

## Uso
```
/gitpush                  # Sincronizza intelligentemente HANDOFF.md con GitHub ed esegue backup
/gitpush --dry-run        # Mostra l'anteprima delle differenze senza inviare
```

## Cosa fa
- Rileva modifiche locali via git status
- Aggiorna README.md e HANDOFF.md
- Crea il commit ed esegue il backup completo su GitHub
