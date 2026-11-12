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
| `/handoff` | Genera HANDOFF.md con riepilogo sessione |
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

## 📝 Handoff

Alla fine di ogni sessione lavorativa:
```bash
/handoff                    # Genera riepilogo
/handoff focus <argomento>  # Con filtro specifico
```

Verrà creato/aggiornato `HANDOFF.md` con:
- Obiettivi completati
- File modificati
- Decisioni prese
- Checklist per sessione successiva