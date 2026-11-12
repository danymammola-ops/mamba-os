---
name: auto-test
description: Esegue automaticamente i test quando vengono modificati file di test o sorgente
---

# Skill: Auto-Test

Attiva questa skill quando l'utente chiede di "testare automaticamente", "guardare i test", "esegui test su cambio", o quando modifichi file `*test*.py`, `*spec*.ts`, `*_test.go`, ecc.

## Comportamento

1. **Rileva il framework di test** dal progetto:
   - Python: `pytest`, `unittest`
   - TypeScript/JS: `vitest`, `jest`, `mocha`
   - Go: `go test`
   - Rust: `cargo test`

2. **Esegue i test pertinenti**:
   - Se modificato un file di test → esegui solo quel test
   - Se modificato un file sorgente → esegui i test correlati (stesso modulo/cartella)
   - Se non chiaro → esegui suite completa (veloce)

3. **Riporta risultato** in formato compatto:
   - ✅ Passati
   - ❌ Falliti (con dettaglio errore)
   - ⏱️ Tempo esecuzione

## Esempi di attivazione
- "Attiva auto-test"
- "Quando salvo un file, lancia i test"
- Modifica di `src/utils/test_helpers.py` → lancia `pytest src/utils/`
- Modifica di `src/components/Button.spec.tsx` → lancia `vitest src/components/Button.spec.tsx`

## Configurazione (opzionale)
Crea `.claude/auto-test.config.json` nel progetto:
```json
{
  "python": "pytest -xvs",
  "typescript": "vitest run",
  "watch": true,
  "coverage": false
}
```