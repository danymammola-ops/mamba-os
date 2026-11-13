# CLAUDE.md - Istruzioni Globali per Claude Code

Questo file definisce come devo comportarmi quando lavoro nel progetto `mio/ai`. Caricato automaticamente all'avvio.

## 🔄 Handoff & GitPush Rules (REGOLA FERREA)
- `/handoff`: Crea o aggiorna **ESCLUSIVAMENTE** il file locale `HANDOFF.md`. **NON fare mai commit, né push, né chiamate API a GitHub**. Rimane al 100% sul computer locale.
- `/handon`: Legge **ESCLUSIVAMENTE** il file locale `HANDOFF.md` per riprendere il contesto di lavoro. Zero rete, zero commit.
- `/gitpush`: È **L'UNICO** comando autorizzato a sincronizzare ed eseguire il backup completo su GitHub. Si attiva **SOLO ED ESCLUSIVAMENTE** quando l'utente digita esplicitamente `/gitpush`.

## 🎯 Obiettivo del Progetto
Sperimentazione, sviluppo e automazione con agenti AI, workflow e tooling avanzato.

## ⚙️ Configurazione Comportamentale

### Modalità Operativa Predefinita
- **Proattivo**: Non aspettare istruzioni passo-passo. Se vedo un pattern, propongo e implemento.
- **Verboso su richiesta**: Spiego il "perché" solo quando chiedi o quando è critico.
- **Workflow-first**: Per task complessi (>3 step), propongo sempre un workflow.

### Linguaggi e Stack Preferiti
- Python (scripting, data, AI/ML)
- TypeScript/JavaScript (tooling, web)
- Bash/PowerShell (automazione sistema)
- Markdown (documentazione)

## 🔧 Tool & Permessi

### Sempre consentiti (no prompt)
- Lettura/Scrittura file in `mio/ai/**`
- Esecuzione comandi `python`, `node`, `npm`, `git`, `gh`
- Glob/Grep/Search nel progetto
- WebFetch/WebSearch per documentazione

### Richiedono conferma
- Comandi distruttivi (`rm -rf`, `git reset --hard`, `docker rm`)
- Modifiche a `settings.json` globali
- Installazione pacchetti globali (`npm i -g`, `pip install --global`)

## 🧠 Skill Attive (Auto-load)
Quando rilevo questi pattern, carico automaticamente la skill:
- `code-review` → `/code-review` su PR/diff
- `dataviz` → grafici, dashboard, analisi dati
- `security-review` → audit codice, vulnerabilità
- `run` → "lancia", "testa", "esegui", "avvia"
- `workflow-authoring` → "workflow", "orchestra", "pipeline"

## 🎪 Workflow Predefiniti
Salva i workflow in `.claude/workflows/`:
- `code-review.yml` — Pipeline review + verifica
- `refactor.yml` — Analisi → Piano → Esecuzione → Test
- `security-audit.yml` — Scan → Classificazione → Fix → Verifica

## 📁 Struttura Progetto Attesa
```
mio/ai/
├── CLAUDE.md           # Questo file
├── .claude/
│   ├── settings.json   # Config locale (hooks, permessi)
│   ├── workflows/      # Workflow YAML/JS
│   ├── skills/         # Skill personalizzate
│   └── memory/         # Memoria persistente
├── scripts/            # Script riutilizzabili
├── docs/               # Documentazione
└── src/                # Codice sorgente principale
```

## 🔑 Parole Chiave Attivatrici (usa nel prompt)
| Parola | Azione |
|--------|--------|
| "workflow" | Lancia orchestrazione multi-agente |
| "review" / "code-review" | Attiva `/code-review` |
| "security" / "vuln" / "audit" | Attiva `/security-review` |
| "visualizza" / "grafico" / "dashboard" | Attiva `/dataviz` |
| "lancia" / "esegui" / "testa" | Attiva `/run` |
| "automatizza" / "hook" / "settings" | Attiva `update-config` |
| "semplifica" / "refactor" / "pulizia" | Attiva `/simplify` |

## 📝 Note Operative
- **Memoria**: Uso `~/.claude/projects/C--Users-danym/memory/` per fatti persistenti
- **Sessioni**: Storico in `~/.claude/sessions/`
- **Plugin**: Marketplace ufficiale già configurato in `~/.claude/plugins/marketplaces/claude-plugins-official/`

## 🚀 Quick Start Commands
```bash
# Code review completo
/code-review max-findings all

# Security audit
/security-review

# Workflow personalizzato
"Esegui un workflow per [task complesso]"

# Lancia progetto
/run
```

---
*Generato automaticamente. Modifica questo file per cambiare il mio comportamento.*
🤖 Generated with [Claude Code](https://claude.com/claude-code)
Co-Authored-By: Claude Code <noreply@anthropic.com>