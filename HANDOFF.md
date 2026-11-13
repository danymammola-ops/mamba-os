# HANDOFF.md

**Data generazione**: 2026-11-13 17:49:36
**Focus**: Ristrutturazione Monorepo MAMBA OS

## 1. Obiettivo e Stato Attuale
**Obiettivo principale**: Sviluppo di MAMBA OS — Sistema Desktop Autonomo Multi-Agente (Orchestratore Antigravity, FreeLLMAPI a costo zero, HUD 3D Verde Smeraldo, User Moves e Claude Code Engine).
**Stato attuale**: ✅ **Ristrutturazione Monorepo completata; fondamenta e comandi globali attivi**.

## 2. File Creati o Modificati
| Data | File | Tipo | Descrizione |
|------|------|------|-------------|
| 2026-11-12 | CLAUDE.md | config | Istruzioni globali progetto |
| 2026-11-12 | .claude/settings.json | config | Configurazione hooks e permessi |
| 2026-11-12 | .claude/skills/*.md | skill | Skill personalizzate (auto-test, github-automation, project-init) |
| 2026-11-12 | .claude/workflows/*.yml | workflow | Workflow YAML (code-review, refactor, security-audit) |
| 2026-11-13 | .claude/settings.json | config | Aggiunto GITHUB_TOKEN per automazione GitHub |
| 2026-11-13 | HANDOFF.md | docs | Aggiornato con task completati |
| 2026-11-13 | scripts/gitupdate.py | script | Sync intelligente HANDOFF.md |
| 2026-11-13 | .claude/skills/gitupdate.md | skill | Documentazione skill gitupdate |
| 2026-11-13 | CLAUDE.md | config | Istruzioni globali progetto |
| 2026-11-13 | .claude/skills/*.md | skill | Skill personalizzate (auto-test, github-automation, project-init) |
| 2026-11-13 | .claude/workflows/*.yml | workflow | Workflow YAML (code-review, refactor, security-audit) |
| 2026-11-12 | .claudeignore | config | Esclusione file pesanti (node_modules, build, venv) per risparmio token |
| 2026-11-13 | .claude/commands/handoff.md | command | Comando `/handoff` (salva la sessione localmente in HANDOFF.md) |
| 2026-11-13 | .claude/commands/handon.md | command | Comando `/handon` (legge HANDOFF.md e riprende il lavoro) |
| 2026-11-13 | .claude/commands/gitupdate.md | command | Comando `/gitupdate` (merge intelligente e push su GitHub) |
| 2026-11-13 | Desktop/progetti ai/idea automatica.txt | docs | Architettura completa sistema multi-agente Jarvis |
| 2026-11-13 | claude/settings.json | json | Git: M  |
| 2026-11-13 | .claude/skills/gitupdate/SKILL.md | md | Git:  M |
| 2026-11-13 | scripts/handoff_generator.py | py | Git:  M |
| 2026-11-13 | .claude/plugins/marketplaces/claude-plugins-official/plugins/handoff-tool/commands/gitupdate.md | md | Git: ?? |
| 2026-11-13 | README.md | md | Creato/Modificato |
| 2026-11-13 | .claude\agents\handoff.md | md | Creato/Modificato |
| 2026-11-13 | .claude\commands\gitupdate.md | md | Creato/Modificato |
| 2026-11-13 | .claude\commands\handoff.md | md | Creato/Modificato |
| 2026-11-13 | .claude\commands\handon.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\auto-test.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\github-automation.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\project-init.md | md | Creato/Modificato |
| 2026-11-13 | .claude\plugins\marketplaces\claude-plugins-official\plugins\handoff-tool\commands\gitupdate.md | md | Creato/Modificato |
| 2026-11-13 | .claude\plugins\marketplaces\claude-plugins-official\plugins\handoff-tool\commands\handoff.md | md | Creato/Modificato |
| 2026-11-13 | .claude\plugins\marketplaces\claude-plugins-official\plugins\handoff-tool\commands\handon.md | md | Creato/Modificato |
| 2026-11-13 | .claude\sk\ills\handoff\commands\handoff.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\gitupdate\SKILL.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\handoff\SKILL.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\handon\SKILL.md | md | Creato/Modificato |
| 2026-11-13 | scripts\gitupdate.py | py | Creato/Modificato |
| 2026-11-13 | scripts\handoff_generator.py | py | Creato/Modificato |
| 2026-11-13 | scripts\show_handoff.py | py | Creato/Modificato |
| 2026-11-13 | scripts/gitpush.py | script | Sync intelligente HANDOFF.md |
| 2026-11-13 | .claude/skills/gitpush.md | skill | Documentazione skill gitpush |
| 2026-11-13 | .claude/commands/gitpush.md | command | Comando `/gitpush` (merge intelligente e push su GitHub) |
| 2026-11-13 | .claude/skills/gitpush/SKILL.md | md | Git:  M |
| 2026-11-13 | .claude/plugins/marketplaces/claude-plugins-official/plugins/handoff-tool/commands/gitpush.md | md | Git: ?? |
| 2026-11-13 | .claude\commands\gitpush.md | md | Creato/Modificato |
| 2026-11-13 | .claude\plugins\marketplaces\claude-plugins-official\plugins\handoff-tool\commands\gitpush.md | md | Creato/Modificato |
| 2026-11-13 | .claude\skills\gitpush\SKILL.md | md | Creato/Modificato |
| 2026-11-13 | scripts\gitpush.py | py | Creato/Modificato |
| 2026-11-13 | .claude/skills/gitpush/ | claude/skills/gitpush/ | Nuovo file |
| 2026-11-13 | gitpush.bat | bat | Nuovo file |
| 2026-11-13 | gitpush.ps1 | ps1 | Nuovo file |
| 2026-11-13 | .claude/sk/ills/handoff/commands/handoff.md | md | Eliminato |
| 2026-11-13 | .claude/skills/github-automation.md | md | Modificato |
| 2026-11-13 | ANDOFF.md | md | Git: M  |
| 2026-11-13 | claude/ | file | Git: ?? |
| 2026-11-13 | freellmapi/ | file | Git: ?? |
| 2026-11-13 | handoff.bat | bat | Git: ?? |
| 2026-11-13 | handoff.ps1 | ps1 | Git: ?? |
| 2026-11-13 | handon.bat | bat | Git: ?? |
| 2026-11-13 | handon.ps1 | ps1 | Git: ?? |
| 2026-11-13 | claude\README.md | md | Creato/Modificato |
| 2026-11-13 | freellmapi\README.md | md | Creato/Modificato |

## 3. Decisioni Chiave e Tentativi Scartati
- Usare skill in `.claude/skills/` invece di plugin globali per maggiore controllo
- Configurare hooks PostToolUse per syntax check automatico Python/TypeScript
- Installare 10 plugin ufficiali dal marketplace
- Non configurare hook pre-commit (troppo invasivi per il flusso lavoro)
- Non usare rm -rf con glob pattern in hook (rischio accidental)

## 4. Checklist Prossimi Passi Concreti
- [x] Creare repository GitHub e push iniziale
- [ ] Testare gitupdate --dry-run e sync reale
- [ ] Configurare GITHUB_TOKEN in settings.json per automazione GitHub
- [ ] Testare hook syntax check modificando un file .py o .ts
- [ ] Proviare /code-review su un file esistente
- [ ] Creare un workflow personalizzato in .claude/workflows/
- [ ] Testare le skill installate (auto-test, github-automation)
- [ ] Eseguire test per: test merge intelligente
- [ ] Testare gitpush --dry-run e sync reale

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
*Sessione: c:\Users\danym\mio\ai*
**Comandi Workflow**:
- `/handoff` - Sintetizza la sessione corrente in locale in `HANDOFF.md`
- `/handon` - Legge `HANDOFF.md` e riprende il lavoro all'istante con contesto pulito
- `/gitupdate` - Sincronizza `HANDOFF.md` con GitHub tramite merge intelligente
- `/gitupdate --dry-run` - Mostra l'anteprima delle modifiche senza inviarle
*Generato e verificato automaticamente per la sessione: mio/ai*
- `/gitpush` - Sincronizza `HANDOFF.md` con GitHub tramite merge intelligente
- `/gitpush --dry-run` - Mostra l'anteprima delle modifiche senza inviarle

## 3. Decisioni Chiave e Vincoli Architetturali
- **Separazione Netta Locale vs Remoto**:
- `/handoff` lavora **esclusivamente in locale** su `HANDOFF.md`. Zero chiamate di rete, zero push GitHub.
- `/handon` lavora **esclusivamente in locale** leggendo `HANDOFF.md`.
- `/gitupdate` è **l'unico comando** che sincronizza con GitHub (solo quando invocato esplicitamente).
- **Zero Dipendenze Esterne nel Sync**: `gitupdate.py` usa Python nativo e Git CLI standard, senza dipendere da `gh` o `jq`.
- **Bypass Permessi Attivo**: Claude Code esegue comandi e modifiche senza bloccare l'utente con richieste continue di autorizzazione.
- **Risparmio Token**: Token context pulito aprendo nuove schede con `/handon` dopo ogni `/handoff`.
- `/gitpush` è **l'unico comando** che sincronizza con GitHub (solo quando invocato esplicitamente).
- **Zero Dipendenze Esterne nel Sync**: `gitpush.py` usa Python nativo e Git CLI standard, senza dipendere da `gh` o `jq`.

## 4. Checklist Stato Avanzamento
- [x] Configurato bypassPermissions per esecuzione autonoma di Claude Code
- [x] Connesso GitHub MCP con Personal Access Token
- [x] Implementati e testati comandi globali e locali `/handoff` e `/handon`
- [x] Implementato script `scripts/gitupdate.py` per merge e sync GitHub
- [x] Registrato comando `/gitupdate` nel menu di Claude Code
- [x] Testato sync bidirezionale con GitHub (test completato con successo)
- [x] Redatto documento architettura multi-agente in `Desktop/progetti ai/idea automatica.txt`
- [ ] Avvio Fase 1 del progetto multi-agente "Idea Automatica"
- [x] Implementato script `scripts/gitpush.py` per merge e sync GitHub
- [x] Registrato comando `/gitpush` nel menu di Claude Code
