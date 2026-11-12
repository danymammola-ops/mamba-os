---
name: github-automation
description: Automatizza workflow GitHub: PR, issue, release, branch management
---

# Skill: GitHub Automation

Attiva quando l'utente menziona "PR", "pull request", "issue", "release", "github", "gh cli", "branch", "merge".

## Prerequisiti
- `gh` CLI installato e autenticato (`gh auth login`)
- Repository con remote `origin` su GitHub

## Capabilità

### Branch & PR Management
```bash
# Crea branch feature + PR draft
gh-automation feature "nome-feature" "descrizione"

# Apri PR da branch corrente
gh-automation pr "Titolo PR" "Body con changelog"

# Aggiorna PR esistente
gh-automation pr-update --add-label "review-needed"

# Merge PR (squash/rebase/merge)
gh-automation merge --method squash --delete-branch
```

### Issue Management
```bash
# Crea issue da template
gh-automation issue --template bug_report "Titolo bug"

# Chiudi issue collegato a PR
gh-automation issue-close 123 "Fixed in #456"

# Lista issue assegnate a me
gh-automation my-issues
```

### Release Automation
```bash
# Crea release con changelog auto-generato
gh-automation release v1.2.0 --generate-notes

# Draft release da tag
gh-automation release-draft v1.2.0
```

### Workflow Trigger
```bash
# Trigger workflow manualmente
gh-automation workflow-run ci.yml --ref main

# Monitora workflow run
gh-automation workflow-watch <run-id>
```

## Hooks Integrati (in settings.json)
- **Post-commit**: Auto-push branch feature
- **Post-PR-create**: Assegna reviewer, aggiungi label
- **Post-merge**: Cleanup branch, aggiorna changelog

## Configurazione
Crea `.claude/github-automation.json`:
```json
{
  "defaultBranch": "main",
  "prTemplate": ".github/PULL_REQUEST_TEMPLATE.md",
  "issueTemplates": ".github/ISSUE_TEMPLATE/",
  "autoAssign": true,
  "autoLabel": true,
  "deleteBranchOnMerge": true
}
```