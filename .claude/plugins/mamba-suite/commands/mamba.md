---
name: mamba
description: Esegue richieste desktop e compiti tramite la Console di Collegamento Mamba OS (Zero Token per testo, micro-agenti per app)
argument-hint: "<richiesta o comando>"
allowed-tools: Bash, Read
---

# Mamba OS — Console Gateway

Invia la richiesta direttamente alla Console di Collegamento di Mamba OS:
- Se la richiesta è di **puro testo/chat/traduzione**: la risponde FreeLLMAPI a 0 token.
- Se la richiesta è di **automazione desktop** (WhatsApp, Meet, Spotify, finestre): attiva i micro-agenti con Safety Gate.

```bash
python mamba/console.py "$ARGUMENTS"
```
