# HANDOFF.md

**Data generazione**: 2026-11-12 22:10:26
**Focus**: Nessuno

## 1. Obiettivo e Stato Attuale

**Obiettivo principale**: Sviluppo e configurazione di Claude Code con workflow, skill e plugin
**Stato attuale**: Configurazione completata

## 2. File Creati o Modificati

| Data | File | Tipo | Descrizione |
|------|------|------|-------------|
| 2026-11-12 | CLAUDE.md | config | Istruzioni globali progetto |
| 2026-11-12 | .claude/settings.json | config | Configurazione hooks e permessi |
| 2026-11-12 | .claude/skills/*.md | skill | Skill personalizzate (auto-test, github-automation, project-init) |
| 2026-11-12 | .claude/workflows/*.yml | workflow | Workflow YAML (code-review, refactor, security-audit) |

## 3. Decisioni Chiave e Tentativi Scartati

### ✅ Decisioni Prese
- Usare skill in `.claude/skills/` invece di plugin globali per maggiore controllo
- Configurare hooks PostToolUse per syntax check automatico Python/TypeScript
- Installare 10 plugin ufficiali dal marketplace

### ❌ Tentativi Scartati / Errori da Evitare
- Non configurare hook pre-commit (troppo invasivi per il flusso lavoro)
- Non usare rm -rf con glob pattern in hook (rischio accidental)

## 4. Checklist Prossimi Passi Concreti

- [ ] Configurare GITHUB_TOKEN in settings.json per automazione GitHub
- [ ] Testare hook syntax check modificando un file .py o .ts
- [ ] Proviare /code-review su un file esistente
- [ ] Creare un workflow personalizzato in .claude/workflows/
- [ ] Testare le skill installate (auto-test, github-automation)

## 5. Skill e Comandi Consigliati

**Skill installate**:
- `/code-review` - Code review multi-agente
- `/security-review` - Security audit
- `/run` - Esecuzione progetti
- `/loop` - Task ripetitivi

**Comandi utili**:
```bash
/claude plugin list         # Vedere plugin installati
/claude plugin install <nombre>@claude-plugins-official  # Installare nuovi plugin
```

**Workflow pronti all'uso**:
- code-review.yml → Review completo codice
- refactor.yml → Refactoring guidato
- security-audit.yml → Security pipeline

---
*Generato automaticamente da handoff.py*
*Sessione: C:\Users\danym\mio\ai*
