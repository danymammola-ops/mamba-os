---
name: handon
description: Read and resume from HANDOFF.md to continue work with a fresh context.
argument-hint: "[section]"
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash
---

# Resume Work from Handoff (handon)

Read and process the `HANDOFF.md` document from the current project root (or `%TEMP%\HANDOFF.md`).

1. Check if `HANDOFF.md` exists. If not found, instruct the user to run `/handoff` first.
2. Read `HANDOFF.md` and present:
   - Current project status and what was previously accomplished.
   - Key architectural decisions and constraints.
   - The checklist of immediate next steps.
3. Ask the user if they want to start immediately on the first pending item from the checklist.
