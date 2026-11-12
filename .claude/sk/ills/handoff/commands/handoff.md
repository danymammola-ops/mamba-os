---
name: handoff
description: Riassumi la sessione corrente e salva in HANDOFF.md
---

# Comando: /handoff

## Uso
```
/handoff                    # Handoff generale
/handoff focus <argomento>  # Handoff filtrato per topic
```

## Descrizione
Questo comando crea/riassume la sessione corrente in un file HANDOFF.md nella root del progetto.

## Cosa fa
1. **Analizza il contesto corrente**: CLAUDE.md, TODOs, file aperti
2. **Genera lo stato attuale**: obiettivi, progresso, pending tasks
3. **Crea la checklist**: task da completare
4. **Eclude dati sensibili**: chiavi, token, credenziali
5. **Salva in HANDOFF.md**: struttura ordinata e leggibile

## Esempi
```bash
/handoff                           # Handoff completo
/handoff focus login              # Solo su login/auth
/handoff focus feature-user       # Solo su user feature
```