# FreeLLMAPI Gateway

Modulo e configurazione del gateway locale **FreeLLMAPI** (in ascolto su `http://127.0.0.1:31415`).

## Caratteristiche
- **100% Gratuito**: Aggrega e ruota automaticamente i piani gratuiti di oltre 100+ modelli AI (Google Gemini, Groq, Cerebras, Mistral, OpenRouter).
- **Zero Costi Token**: Fornisce token illimitati sia per l'orchestrazione di **MAMBA OS**, sia per **Claude Code**, sia per le chiamate dirette.
- **Failover Automatico**: Se un provider finisce la quota oraria o giornaliera, passa automaticamente al provider di riserva in millisecondi.
- **Auto-Discovery**: I moduli di MAMBA leggono le credenziali direttamente dal database locale SQLite `freeapi.db`.
