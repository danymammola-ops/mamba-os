# HANDOFF.md

**Data aggiornamento**: 2026-11-24
**Focus**: MAMBA OS v2.0 — Neural Cockpit, Galaxy 3D, Secondo Cervello, Edge-TTS & Codex MiniPet

## 1. Obiettivo e Stato Attuale
- **Obiettivo**: Evoluzione completa di Mamba OS in un cockpit cognitivo connesso a `ObsidianVault` (SQLite FTS5 + Galaxy 3D), Claude Code + PowerShell, Voce Neurale Edge-TTS con coda non-interrompente, Pixel Snake slither L→R e Codex-style MiniPet.
- **Stato**: ✅ **Completato, testato end-to-end e sincronizzato su GitHub (`origin/main`)**.

## 2. Principali Componenti Aggiornati
| File | Ruolo |
| :--- | :--- |
| `mamba/ui/index.html`, `styles.css`, `app.js` | Neural Cockpit v2.0 glassmorphism con 4 tab (`Neural Core`, `Galaxy 3D`, `Cervello`, `Claude & Terminale`) |
| `mamba/ui/galaxy.html`, `galaxy.js` | Galaxy View 3D a 60 FPS collegata in tempo reale a `brain.db` |
| `mamba/ui/snake.js` | Pixel-Art Cobra (`idle`), serpente pixelato veloce da sinistra a destra (`thinking`), equalizzatore audio (`speaking`) |
| `mamba/voice/tts_engine.py` | Servizio Edge-TTS Neurale Italiano (`Giuseppe`, `Diego`, `Isabella`, `Elsa`) con cache locale + coda non-bloccante |
| `mamba/ui/desktop_pet.py` | Floating Pixel Pet single-instance con hot-reload, filtri per app Windows attive, stili e dimensioni configurabili |
| `mamba/core/brain_bridge.py` | Bridge `<20ms` verso `C:\Users\danym\Documents\ObsidianVault` + sync Token Guard |
| `mamba/agents/apps/system_agent.py` | App launcher esteso (`obsidian`, `galaxy`, `github`, `freellmapi`, `vault`) + Claude Code stdin bridge |
| `mamba/ui/server.py` | `ThreadingHTTPServer` con API Brain, TTS, Pet PID manager, Claude, Terminal e GitHub sync |

## 3. Verifiche Eseguite
- `test_brain.py`: `3/3` OK.
- Verifica live browser su `http://127.0.0.1:5173/` (`FreeLLM (98)`, `Brain 37n · 244l`, `/api/command`, `/api/tts`, tab `Galaxy 3D`, drawer `Mini & Pets`): 0 errori JS/HTTP.
