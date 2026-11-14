# ⛽ FreeLLMAPI Gateway & Setup

FreeLLMAPI è il gateway locale (open-source, licenza MIT) che aggrega e fa ruotare automaticamente i piani gratuiti di oltre 30+ provider AI, fornendo oltre 100+ modelli accessibili dietro un singolo endpoint locale OpenAI-compatibile.

---

## 📥 Download per Windows e macOS

Scarica sempre l'ultima versione ufficiale dalla pagina Release di GitHub:  
👉 **[FreeLLMAPI Official Releases ↗](https://github.com/tashfeenahmed/freellmapi/releases/latest)**

| Sistema Operativo | Pacchetto di Installazione | Note di Installazione |
|-------------------|----------------------------|-----------------------|
| 🪟 **Windows** | `FreeLLMAPI-Setup-<versione>.exe` | Installazione in 1 clic. Non richiede diritti di amministratore. Opzione `/S` per installazione silenziosa. |
| 🍎 **macOS (Apple Silicon)** | `FreeLLMAPI-<versione>-arm64.dmg` | Per tutti i Mac con chip M1, M2, M3 o M4. Apri il `.dmg` e copia l'app in *Applicazioni*. |
| 🍏 **macOS (Intel)** | `FreeLLMAPI-<versione>.dmg` | Per Mac con processore Intel x86_64. Apri il `.dmg` e copia l'app in *Applicazioni*. |
| 🐧 **Linux** | `FreeLLMAPI-<versione>.AppImage` | Rendi il file eseguibile (`chmod +x`) e avvialo. |

---

## ⚙️ Guida alla Configurazione Rapida (1 Minuto)

1. **Avvio dell'Applicazione**:
   - Avvia FreeLLMAPI. L'app resta attiva in background con un'icona vicino all'orologio di Windows o nella barra di stato di macOS.
2. **Accesso alla Dashboard**:
   - Apri il browser all'indirizzo [http://localhost:3001](http://localhost:3001) (o clicca con il tasto destro sull'icona e scegli *Open Dashboard*).
3. **Inserimento Chiavi Gratuite (Scheda "Keys")**:
   - Più chiavi gratuite aggiungi, più modelli e quote di riserva avrai a disposizione:
     * **[Google AI Studio ↗](https://aistudio.google.com/apikey)**: Fornisce Gemini 2.5 Flash / Pro (limiti molto generosi, gratis).
     * **[Groq Cloud ↗](https://console.groq.com/keys)**: Fornisce Llama 3.3 70B ad altissima velocità.
     * **[Cerebras ↗](https://cloud.cerebras.ai/)**: Latenze record per compiti immediati.
     * **[OpenRouter ↗](https://openrouter.ai/settings/keys)**: Modelli open source gratuiti.
     * **[Mistral AI ↗](https://console.mistral.ai/api-keys)**: Modelli Mistral / Codestral.
4. **Auto-Discovery in Mamba OS**:
   - Non devi copiare token o impostare file `.env` a mano: il modulo `mamba/core/freellm_client.py` legge in automatico il token SQLite locale dal file `%APPDATA%\FreeLLMAPI\freeapi.db`.
