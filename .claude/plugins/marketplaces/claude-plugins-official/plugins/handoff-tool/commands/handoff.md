---
name: handoff
description: Genera HANDOFF.md con riepilogo della sessione corrente
---

# Comando: /handoff

## Uso
```
/handoff                       # Genera HANDOFF.md completo
/handoff focus <argomento>     # Handoff filtrato per topic
```

## Cosa fa
- Riassume obiettivi e stato attuale
- Elenca file creati/modificati
- Documenta decisioni chiave e errori evitare
- Genera checklist prossimi passi
- Elenca skill/comandi consigliati
- **Esclude automaticamente dati sensibili** (API keys, token, password)

## Esempi
```bash
/handoff                    # Handoff completo
/handoff focus workflow     # Solo su workflow
/handoff focus login        # Solo su autenticazione
```

## Output
File `HANDOFF.md` nella root del progetto con struttura ordinata:
1. Obiettivo e Stato Attuale
2. File Creati o Modificati
3. Decisioni Chiave e Tentativi Scartati
4. Checklist Prossimi Passi Concreti
5. Skill e Comandi Consigliati

---
*Mandato dal plugin handoff-tool*