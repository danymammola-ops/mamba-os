---
name: handon
description: Mostra e riprende il contenuto di HANDOFF.md per continuare il lavoro
argumentHint: "[sezione]"
---

# Comando: /handon

## Uso
```
/handon                     # Mostra HANDOFF.md e riassume lo stato per ripartire
/handon <sezione>           # Mostra solo una sezione specifica
```

## Cosa fa
- Legge il file `HANDOFF.md` nella root del progetto o in `%TEMP%`
- Riassume gli obiettivi e cosa è stato fatto
- Evidenzia le decisioni architetturali e i vincoli
- Mostra la checklist dei prossimi passi concreti
- Chiede all'utente se partire subito dal primo punto

---
*Mandato dal plugin handoff-tool*
