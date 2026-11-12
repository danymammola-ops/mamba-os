---
name: project-init
description: Inizializza un nuovo progetto con struttura standard, config, CI/CD
---

# Skill: Project Init

Attiva quando l'utente dice "inizia un progetto", "nuovo progetto", "setup progetto", "scaffolding".

## Cosa fa

Crea struttura completa per progetto Python/TypeScript/Full-stack:

```
project-name/
├── .github/workflows/     # CI/CD
├── .claude/               # Config Claude Code
├── src/                   # Codice sorgente
├── tests/                 # Test
├── docs/                  # Documentazione
├── scripts/               # Script utilità
├── pyproject.toml / package.json
├── README.md
├── LICENSE
├── .gitignore
├── .pre-commit-config.yaml
└── CLAUDE.md
```

## Template disponibili

| Template | Stack | Comando |
|----------|-------|---------|
| `python-cli` | Python + Click + pytest | `project-init python-cli mio-tool` |
| `python-api` | FastAPI + SQLAlchemy + pytest | `project-init python-api mia-api` |
| `ts-node` | TypeScript + Node + vitest | `project-init ts-node mio-script` |
| `react-vite` | React + Vite + Vitest + TS | `project-init react-vite mia-app` |
| `fullstack` | FastAPI + React + Docker | `project-init fullstack mio-progetto` |

## Workflow inclusi
- `ci.yml` — Test + Lint + Type-check
- `release.yml` — Build + Publish + Tag
- `dependabot.yml` — Aggiornamenti automatici

## Pre-commit hooks
- `ruff` / `eslint` — Lint
- `mypy` / `tsc` — Type check
- `pytest` / `vitest` — Test rapidi
- `black` / `prettier` — Format