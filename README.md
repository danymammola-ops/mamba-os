# Progetto AI & Claude Code

Progetto per sperimentazione e sviluppo con Claude Code integrato, workflow e tool avanzati.

## 🚀 Primi Passi

### Configurazione iniziale
```bash
# 1. Verifica le skill
ls .claude/skills/

# 2. Verifica i workflow
ls .claude/workflows/

# 3. Verifica i plugin installati
claude plugin list
```

## 🛠️ Comandi Principali

| Comando | Descrizione |
|---------|-------------|
| `/handoff` | Salva la sessione in locale in HANDOFF.md |
| `/handon` | Legge HANDOFF.md e riprende il lavoro con contesto pulito |
| `/gitupdate` | Aggiorna README.md ed esegue il backup completo su GitHub |
| `/code-review max-findings all` | Code review completa |
| `/security-review` | Security audit |
| `/run` | Lancia il progetto |
| `/loop 5m git status` | Monitoraggio periodico |

## 📂 Struttura Progetto

```
.
├── CLAUDE.md                    # Istruzioni globali
├── HANDOFF.md                   # Sessione riepilogo (generato)
├── .claude/
│   ├── settings.json            # Config locale
│   ├── skills/                  # Skill personalizzate
│   ├── workflows/               # Workflow YAML
│   └── agents/                  # Agenti specializzati
├── scripts/
│   └── handoff_generator.py     # Generatore HANDOFF.md
├── docs/                        # Documentazione
└── src/                         # Codice sorgente
```

## 🔧 Skill Installate

| Skill | Uso |
|-------|-----|
| `auto-test` | Test automatici su cambio file |
| `github-automation` | Automazione GitHub (PR, issue) |
| `project-init` | Scaffolding nuovi progetti |
| `handoff` | Riepilogo sessione |

## 📊 Workflow Disponibili

1. **code-review.yml** → Review multi-dimensionale
2. **refactor.yml** → Refactoring incrementale
3. **security-audit.yml** → Security pipeline

## 🔐 Dati Sensibili

⚠️ **NON** aggiungere mai API keys, token o password in questo progetto.  
Usa variabili d'ambiente o file `.env` fuori dal versionamento.

## 📄 Workflow di Sessione & Backup

Questo progetto utilizza il ciclo di sessione a 3 comandi per azzerare il consumo di token e mantenere la repository GitHub come **copia di backup identica del progetto locale**:

| Comando | Descrizione | Ambito |
|---------|-------------|--------|
| `/handoff [focus]` | Salva e sintetizza la sessione corrente in locale in `HANDOFF.md` | **100% Locale** (zero chiamate di rete) |
| `/handon [sezione]` | Legge `HANDOFF.md` e riprende il lavoro all'istante con contesto pulito | **100% Locale** |
| `/gitupdate` | Rileva modifiche, aggiorna `README.md` e carica tutto su GitHub | **Remoto** (Backup Completo) |
| `/gitupdate --dry-run` | Mostra l'anteprima dei file e delle modifiche senza inviarle | Anteprima |

---

## 📌 Stato del Progetto & Avanzamento (Sincronizzato da HANDOFF.md)

*Ultimo aggiornamento: 2026-11-13 16:13:27*

**Obiettivo principale**: Configurare Claude Code per operare in autonomia (zero prompt permessi), integrare GitHub MCP e credenziali, implementare il workflow Handoff/Handon con sincronizzazione intelligente (`/gitupdate`) e progettare l'architettura Desktop Multi-Agente ("Idea Automatica").  
**Stato attuale**: ✅ **Tutti i componenti configurati, testati e funzionanti al 100%**.

### 📁 Ultimi File Modificati / Rilevati nel Progetto:
| Data | File | Tipo | Descrizione |
|------|------|------|-------------|
| 2026-11-13 | .claude\skills\gitupdate\SKILL.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\handoff\SKILL.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\handon\SKILL.md | md | Creato/Modificato |
| 2026-11-13 | scripts\gitupdate.py | py | Creato/Modificato |
| 2026-11-13 | scripts\handoff_generator.py | py | Creato/Modificato |
| 2026-11-13 | scripts\show_handoff.py | py | Creato/Modificato |

### Checklist Prossimi Passi:
- [x] Creare repository GitHub e push iniziale
- [ ] Testare gitupdate --dry-run e sync reale
- [ ] Configurare GITHUB_TOKEN in settings.json per automazione GitHub
- [ ] Testare hook syntax check modificando un file .py o .ts
- [ ] Proviare /code-review su un file esistente
- [ ] Creare un workflow personalizzato in .claude/workflows/
- [ ] Testare le skill installate (auto-test, github-automation)
- [ ] Eseguire test per: test merge intelligente
- [x] Configurato bypassPermissions per esecuzione autonoma di Claude Code
- [x] Connesso GitHub MCP con Personal Access Token
- [x] Implementati e testati comandi globali e locali `/handoff` e `/handon`
- [x] Implementato script `scripts/gitupdate.py` per merge e sync GitHub
- [x] Registrato comando `/gitupdate` nel menu di Claude Code
- [x] Testato sync bidirezionale con GitHub (test completato con successo)
- [x] Redatto documento architettura multi-agente in `Desktop/progetti ai/idea automatica.txt`
- [ ] Avvio Fase 1 del progetto multi-agente "Idea Automatica"
