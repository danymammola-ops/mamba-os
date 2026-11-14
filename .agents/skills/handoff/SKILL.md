---
name: handoff
description: Riassunto sessione e salvataggio stato lavoro in HANDOFF.md con esclusione dati sensibili
---

# Skill: Handoff

Attiva quando l'utente digita `/handoff` o `/handoff focus <argomento>`.

## 🎯 Obiettivo

Creare un file `HANDOFF.md` nella root del progetto che riassuma completamente la sessione corrente, con stato attuale, file modificati, decisioni chiave e checklist per la sessione successiva.

## 📋 Struttura HANDOFF.md

Il file generato conterrà:

1. **Obiettivo e Stato Attuale**
   - Obiettivo principale della sessione
   - Stato attuale (completato/in corso/blocked)

2. **File Creati o Modificati**
   - Elenco ordinato per data
   - Tipologia (creazione/modifica/deletion)
   - Descrizione breve

3. **Decisioni Chiave e Tentativi Scartati**
   - Decisioni architetturali prese
   - Approcci tentati ma scartati
   - Errori commessi e da evitare

4. **Checklist Prossimi Passi Concreti**
   - Task ordinati per priorità
   - Con indicazioni di comando/skill utilizzabili

5. **Skill e Comandi Consigliati**
   - Skill utilizzate durante la sessione
   - Comandi hooks
   - Strumenti specifici per i task rimanenti

## ⚙️ Funzionalità

### Syntax Base
```bash
/handoff
```
Genera HANDOFF.md con stato corrente

### Con Argomento Focus
```bash
/handoff focus sul login
/handoff focus autenticazione
/handoff focus feature X
```
Filtra il riassunto sul topic specificato, mostrando solo informazioni rilevanti

## 🔒 Esclusione Dati Sensibili

Il file HANDOFF.md esclude automaticamente:
- Chiavi API (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.)
- Token (`GITHUB_TOKEN`, `PAT`, `SECRET`, `PASSWORD`)
- Chiavi di accesso (`PRIVATE_KEY`, `CLIENT_SECRET`)
- Qualsiasi cosa che contenga `secret`, `key`, `password`, `token`, `credential`

## 📝 Uso Concreto

Esegui direttamente lo script Python generato:

```bash
# Handoff generale
./scripts/handoff_generator.py

# Con focus
./scripts/handoff_generator.py "workflow"
./scripts/handoff_generator.py "login"
```

## 🎯 Esempi di Uso

1. **Handoff generale**: `/handoff`
2. **Handoff su login**: `/handoff focus login`
3. **Handoff su feature**: `/handoff focus feature-user-auth`

## 🛠️ Implementazione Tecnica

Lo script `scripts/handoff_generator.py`:
1. Analizza il file `./AGENTS.md` per obiettivi
2. Elenca i file nella cartella `.Codex/skills/`, `.Codex/workflows/`
3. Genera checklist logica per prossimi passi
4. Purifica da dati sensibili (API key, token)
5. Scrive HANDOFF.md ordinato e leggibile