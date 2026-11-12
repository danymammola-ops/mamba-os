#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Mostra il contenuto di HANDOFF.md in modo ordinato
.DESCRIPTION
    Legge e visualizza HANDOFF.md generato da handoff_generator.py
.EXAMPLE
    .\scripts\show_handoff.ps1
    Mostra tutto il riepilogo HANDOFF.md
#>

$handoffFile = "$PSScriptRoot\..\HANDOFF.md"

if (-not (Test-Path $handoffFile)) {
    Write-Host "❌ File HANDOFF.md non trovato in: (Resolve-Path $handoffFile).Parent" -ForegroundColor Red
    Write-Host "Esegui prima '.\\scripts\\handoff.ps1' per generarlo" -ForegroundColor Yellow
    exit 1
}

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "HANDDOFF - Sessione Riepilogo" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

Get-Content $handoffFile