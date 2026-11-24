/**
 * mamba/ui/app.js - Controller Mamba OS v2.0
 * - VoiceMouth Edge-TTS Neurale con coda stretta (non interrompe mai la lettura in corso!)
 * - Pixel Snake reattivo (striscia veloce L->R quando elabora/scrive, equalizzatore quando parla)
 * - Switcher integrato: Core, Galaxy 3D, Secondo Cervello, Claude Code + Terminale + GitHub
 * - Codex-style Mini & Pets sincronizzato live con pet_config.json
 */

class VoiceMouth {
    constructor({ onStart, onLevel, onEnd, onQueueChange, onLog }) {
        this.onStart = onStart;
        this.onLevel = onLevel;
        this.onEnd = onEnd;
        this.onQueueChange = onQueueChange;
        this.onLog = onLog;

        this.enabled = true;
        this.voice = 'it-IT-GiuseppeMultilingualNeural';
        this.queue = [];
        this.playing = null;
        this.generation = 0;

        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.analyser = this.ctx.createAnalyser();
        this.analyser.fftSize = 512;
        this.gain = this.ctx.createGain();
        this.gain.gain.value = 1.25;
        this.gain.connect(this.analyser);
        this.analyser.connect(this.ctx.destination);
        this.samples = new Float32Array(this.analyser.fftSize);
        this._meterLoop();
    }

    get busy() {
        return !!this.playing || this.queue.length > 0;
    }

    setEnabled(val) {
        this.enabled = !!val;
        if (!this.enabled) this.stopAll();
    }

    setVoice(voiceId) {
        if (voiceId) this.voice = voiceId;
    }

    /**
     * NON interrompe mai la voce in corso! Accoda la nuova risposta.
     */
    enqueue(text) {
        if (!this.enabled || !text || !text.trim()) return;
        const clean = text.replace(/[*_#`>\[\]()]/g, ' ').replace(/\s+/g, ' ').trim();
        if (!clean) return;

        const audioPromise = this._fetchTTS(clean, this.voice);
        this.queue.push({ text: clean, audioPromise });
        this.onQueueChange?.(this.queue.length + (this.playing ? 1 : 0));
        this._drain();
    }

    async _fetchTTS(text, voice) {
        try {
            const resp = await fetch('/api/tts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, voice, rate: '+4%' }),
            });
            if (!resp.ok) throw new Error(`TTS HTTP ${resp.status}`);
            const buf = await resp.arrayBuffer();
            return await this.ctx.decodeAudioData(buf);
        } catch (err) {
            this.onLog?.(`TTS Neurale fallback: ${err.message}`, 'warn');
            return null;
        }
    }

    async _drain() {
        if (this.playing || this.queue.length === 0) {
            if (!this.playing && this.queue.length === 0) {
                this.onQueueChange?.(0);
                this.onEnd?.();
            }
            return;
        }

        const gen = this.generation;
        const item = this.queue.shift();
        this.playing = item;
        this.onQueueChange?.(this.queue.length + 1);
        this.onStart?.();

        if (this.ctx.state !== 'running') {
            await this.ctx.resume().catch(() => {});
        }

        const buffer = await item.audioPromise;
        if (gen !== this.generation) return;

        if (buffer) {
            const src = this.ctx.createBufferSource();
            src.buffer = buffer;
            src.connect(this.gain);
            item.src = src;
            src.onended = () => {
                if (gen === this.generation) {
                    this.playing = null;
                    this._drain();
                }
            };
            src.start();
        } else {
            // Fallback solo se Edge-TTS non raggiungibile
            if ('speechSynthesis' in window) {
                const u = new SpeechSynthesisUtterance(item.text);
                u.lang = 'it-IT';
                const done = () => {
                    if (gen === this.generation) {
                        this.playing = null;
                        this._drain();
                    }
                };
                u.onend = done;
                u.onerror = done;
                window.speechSynthesis.speak(u);
            } else {
                this.playing = null;
                this._drain();
            }
        }
    }

    /** Chiamata solo se l'utente preme esplicitamente il pulsante Stop */
    stopAll() {
        this.generation++;
        this.queue.length = 0;
        try { this.playing?.src?.stop(); } catch {}
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        this.playing = null;
        this.onQueueChange?.(0);
        this.onEnd?.();
    }

    _meterLoop() {
        const tick = () => {
            let level = 0;
            if (this.playing?.src) {
                this.analyser.getFloatTimeDomainData(this.samples);
                let sum = 0;
                for (let i = 0; i < this.samples.length; i++) sum += this.samples[i] * this.samples[i];
                level = Math.min(1, Math.sqrt(sum / this.samples.length) * 4.5);
            }
            this.onLevel?.(level);
            requestAnimationFrame(tick);
        };
        requestAnimationFrame(tick);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const snake = new MambaSnake('snake-canvas');
    const miniPet = new MiniPetPreview('mini-pet-preview-canvas');

    const logsContainer = document.getElementById('logs-container');
    const chatFeed = document.getElementById('chat-feed');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const snakeBadge = document.getElementById('snake-state-badge');
    const voiceQueuePill = document.getElementById('voice-queue-pill');
    const btnVoiceStop = document.getElementById('btn-voice-stop');
    const btnVoiceToggle = document.getElementById('btn-voice-toggle');
    const voiceSelect = document.getElementById('voice-select');

    let currentMode = 'auto';
    let galaxyLoaded = false;

    function addLog(text, level = 'info') {
        const t = new Date().toTimeString().split(' ')[0];
        const div = document.createElement('div');
        div.className = `log-row ${level}`;
        div.innerHTML = `<span class="log-time">[${t}]</span>${escapeHtml(text)}`;
        logsContainer.appendChild(div);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    function escapeHtml(s) {
        return String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    }

    function formatMsgText(s) {
        return escapeHtml(s)
            .replace(/\*\*([^*]+)\*\*/g, '<b>$1</b>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    function setSnakeUIState(st) {
        if (st === 'thinking') {
            snake.setState('thinking');
            snakeBadge.innerText = '⚡ SLITHER // ELABORAZIONE...';
        } else if (st === 'speaking') {
            snake.setState('speaking');
            snakeBadge.innerText = '🔊 SPEAKING // VOCE NEURALE';
        } else {
            snake.setState('idle');
            snakeBadge.innerText = '● IDLE // READY';
        }
    }

    // Orologio
    setInterval(() => {
        document.getElementById('clock-display').innerText = new Date().toTimeString().split(' ')[0];
    }, 1000);

    // Voice Engine con coda stretta (non interrompe mai la lettura in corso!)
    const mouth = new VoiceMouth({
        onStart: () => {
            if (snake.state !== 'thinking') setSnakeUIState('speaking');
            btnVoiceStop.style.display = 'inline-flex';
        },
        onLevel: (lvl) => snake.setAudioLevel(lvl),
        onEnd: () => {
            if (snake.state !== 'thinking') setSnakeUIState('idle');
            btnVoiceStop.style.display = 'none';
        },
        onQueueChange: (count) => {
            if (count > 0) {
                voiceQueuePill.innerText = `🔊 Lettura (${count} in coda)`;
                voiceQueuePill.classList.add('visible');
            } else {
                voiceQueuePill.classList.remove('visible');
            }
        },
        onLog: addLog,
    });

    voiceSelect.addEventListener('change', () => {
        mouth.setVoice(voiceSelect.value);
        addLog(`Voce Neurale impostata: ${voiceSelect.selectedOptions[0].text}`, 'info');
    });
    btnVoiceToggle.addEventListener('click', () => {
        mouth.setEnabled(!mouth.enabled);
        btnVoiceToggle.innerText = mouth.enabled ? '🔊 ON' : '🔇 OFF';
        btnVoiceToggle.classList.toggle('accent', mouth.enabled);
    });
    btnVoiceStop.addEventListener('click', () => {
        mouth.stopAll();
        addLog('Voce interrotta manualmente.', 'warn');
    });

    // Navigation Tabs
    const navTabs = document.querySelectorAll('.nav-tab');
    const viewPanes = document.querySelectorAll('.view-pane');
    function switchTab(viewId) {
        navTabs.forEach(t => t.classList.toggle('active', t.dataset.view === viewId));
        viewPanes.forEach(p => p.classList.toggle('active', p.id === viewId));
        if (viewId === 'view-galaxy' && !galaxyLoaded) {
            document.getElementById('galaxy-iframe').src = '/galaxy.html?embed=1';
            galaxyLoaded = true;
        }
        if (viewId === 'view-claude') refreshGitHubStatus();
    }
    navTabs.forEach(tab => tab.addEventListener('click', () => switchTab(tab.dataset.view)));
    document.getElementById('badge-brain').addEventListener('click', () => switchTab('view-brain'));
    document.getElementById('badge-github').addEventListener('click', () => switchTab('view-claude'));

    // Mode Pills
    document.querySelectorAll('.mode-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            document.querySelectorAll('.mode-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            currentMode = pill.dataset.mode;
            addLog(`Modalità router: [${currentMode.toUpperCase()}]`, 'info');
        });
    });

    // App Launcher
    window.launchApp = async function(app) {
        addLog(`Avvio rapido: ${app}`, 'info');
        await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: `apri ${app}`, mode: 'auto' }),
        });
    };

    // Append message to chat
    function appendChatMsg(role, text, metaLabel = '') {
        const div = document.createElement('div');
        div.className = `msg ${role}`;
        if (role === 'assistant') {
            div.innerHTML = `
                <div class="msg-meta">
                    <span class="msg-route">${escapeHtml(metaLabel)}</span>
                    <button class="msg-replay" title="Rileggi con voce neurale">🔊 Rileggi</button>
                </div>
                <div class="msg-text">${formatMsgText(text)}</div>
            `;
            div.querySelector('.msg-replay').addEventListener('click', () => mouth.enqueue(text));
        } else {
            div.innerHTML = `<div class="msg-text">${escapeHtml(text)}</div>`;
        }
        chatFeed.appendChild(div);
        chatFeed.scrollTop = chatFeed.scrollHeight;
    }

    // Send Command (NON interrompe la voce precedente!)
    async function sendCommand(promptText) {
        const text = (promptText || '').trim();
        if (!text) return;
        userInput.value = '';

        appendChatMsg('user', text);
        addLog(`TU (${currentMode}): "${text}"`, 'info');

        // Avvia l'animazione Pixel Snake che striscia velocemente L -> R!
        setSnakeUIState('thinking');
        const t0 = performance.now();

        try {
            const resp = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text, mode: currentMode }),
            });
            const data = await resp.json();
            const elapsed = ((performance.now() - t0) / 1000).toFixed(2);

            if (data.success) {
                const reply = data.output || 'Completato.';
                appendChatMsg('assistant', reply, `${(data.route || 'auto').toUpperCase()} · ${elapsed}s`);
                addLog(`MAMBA [${data.route}] in ${elapsed}s`, 'info');

                // Accoda la nuova risposta vocale senza tagliare quella in corso!
                if (mouth.enabled) {
                    mouth.enqueue(reply);
                    if (!mouth.playing) setSnakeUIState('idle');
                } else {
                    setSnakeUIState('idle');
                }
            } else {
                appendChatMsg('assistant', `Errore: ${data.error}`, 'ERROR');
                addLog(`ERRORE: ${data.error}`, 'error');
                setSnakeUIState(mouth.busy ? 'speaking' : 'idle');
            }
        } catch (err) {
            appendChatMsg('assistant', `Errore rete: ${err.message}`, 'NETWORK ERROR');
            addLog(`Errore rete: ${err.message}`, 'error');
            setSnakeUIState(mouth.busy ? 'speaking' : 'idle');
        }
    }

    window.quickSend = (txt) => sendCommand(txt);
    sendBtn.addEventListener('click', () => sendCommand(userInput.value));
    userInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') sendCommand(userInput.value);
    });

    // Clear & Copy logs
    document.getElementById('btn-copy-logs').addEventListener('click', () => {
        const txt = Array.from(logsContainer.children).map(n => n.innerText).join('\n');
        navigator.clipboard.writeText(txt).then(() => addLog('Log copiati negli appunti.', 'info'));
    });
    document.getElementById('btn-clear-chat').addEventListener('click', () => {
        logsContainer.innerHTML = '';
        fetch('/api/chat/clear', { method: 'POST' }).catch(() => {});
        addLog('Cronologia chat e log azzerati.', 'warn');
    });

    // Mic STT
    const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRec) {
        const rec = new SpeechRec();
        rec.lang = 'it-IT';
        let active = false;
        rec.onresult = (ev) => {
            const tr = ev.results[0][0].transcript;
            userInput.value = tr;
            sendCommand(tr);
        };
        rec.onend = () => { active = false; micBtn.classList.remove('accent'); };
        micBtn.addEventListener('click', () => {
            if (active) { rec.stop(); return; }
            active = true;
            micBtn.classList.add('accent');
            rec.start();
        });
    } else {
        micBtn.style.opacity = '0.4';
    }

    // =========================================================================
    // TAB 3: SECOND BRAIN SEARCH & CAPTURE
    // =========================================================================
    async function runBrainSearch() {
        const q = document.getElementById('brain-search-input').value.trim();
        const box = document.getElementById('brain-search-results');
        if (!q) return;
        const res = await fetch(`/api/brain/search?q=${encodeURIComponent(q)}`).then(r => r.json());
        const hits = res.results || [];
        box.innerHTML = hits.map(h => `
            <div class="brain-hit" onclick="window.open('obsidian://open?vault=ObsidianVault&file=' + encodeURIComponent('${h.path}'))">
                <div class="brain-hit-title">${escapeHtml(h.title)}</div>
                <div class="brain-hit-path">${escapeHtml(h.path)} · score ${h.score}</div>
                <div class="brain-hit-snip">${escapeHtml(h.summary || h.snippet)}</div>
            </div>
        `).join('') || '<div style="color:var(--muted);font-size:12px;">Nessuna nota trovata.</div>';
    }
    document.getElementById('btn-brain-search').addEventListener('click', runBrainSearch);
    document.getElementById('brain-search-input').addEventListener('keydown', e => { if (e.key === 'Enter') runBrainSearch(); });

    document.getElementById('btn-run-gardener').addEventListener('click', async () => {
        const out = document.getElementById('brain-ops-output');
        out.innerText = '⏳ Esecuzione Nightly Gardener in corso...';
        const res = await fetch('/api/brain/gardener', { method: 'POST' }).then(r => r.json());
        out.innerText = JSON.stringify(res, null, 2);
        refreshTelemetry();
    });

    document.getElementById('btn-cap-inbox').addEventListener('click', async () => {
        const t = document.getElementById('cap-title').value.trim();
        const b = document.getElementById('cap-body').value.trim();
        if (!t && !b) return;
        const res = await fetch('/api/command', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: `salva nel cervello: ${t ? t + ' - ' : ''}${b}` }),
        }).then(r => r.json());
        document.getElementById('brain-ops-output').innerText = res.output || JSON.stringify(res);
        document.getElementById('cap-title').value = '';
        document.getElementById('cap-body').value = '';
        refreshTelemetry();
    });

    document.getElementById('btn-cap-daily').addEventListener('click', async () => {
        const t = document.getElementById('cap-title').value.trim();
        const b = document.getElementById('cap-body').value.trim();
        const txt = [t, b].filter(Boolean).join(': ');
        if (!txt) return;
        const res = await fetch('/api/command', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt: `aggiungi al diario: ${txt}` }),
        }).then(r => r.json());
        document.getElementById('brain-ops-output').innerText = res.output || JSON.stringify(res);
        document.getElementById('cap-title').value = '';
        document.getElementById('cap-body').value = '';
    });

    // =========================================================================
    // TAB 4: CLAUDE CODE + TERMINAL + GITHUB
    // =========================================================================
    window.runQuickTerm = async function(engine, cmd) {
        document.getElementById('term-engine').value = engine;
        document.getElementById('term-input').value = cmd;
        await executeTermTab();
    };

    async function executeTermTab() {
        const engine = document.getElementById('term-engine').value;
        const input = document.getElementById('term-input').value.trim();
        const out = document.getElementById('term-output');
        if (!input) return;
        out.innerText = `⏳ [${engine.toUpperCase()}] Esecuzione: ${input}...\n`;

        const endpoint = engine === 'claude' ? '/api/claude' : '/api/terminal';
        const body = engine === 'claude' ? { prompt: input } : { cmd: input };
        const res = await fetch(endpoint, {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        }).then(r => r.json());

        out.innerText = res.output || res.stdout || res.stderr || res.error || JSON.stringify(res, null, 2);
    }
    document.getElementById('btn-term-run').addEventListener('click', executeTermTab);
    document.getElementById('term-input').addEventListener('keydown', e => { if (e.key === 'Enter') executeTermTab(); });

    async function refreshGitHubStatus() {
        try {
            const gh = await fetch('/api/github/status').then(r => r.json());
            const box = document.getElementById('gh-status-box');
            const dot = document.getElementById('dot-github');
            const txt = document.getElementById('txt-github');
            txt.innerText = gh.dirty_count > 0 ? `Git (${gh.dirty_count})` : 'GitHub OK';
            dot.classList.toggle('warn', gh.dirty_count > 0);
            box.innerText = [
                `Branch: ${gh.branch}`,
                `Remote: ${gh.remote}`,
                `File modificati/nuovi: ${gh.dirty_count}`,
                ...(gh.changed_files || []).slice(0, 12),
                '',
                'Ultimi Commit:',
                ...(gh.recent_commits || []),
            ].join('\n');
        } catch {}
    }
    document.getElementById('btn-gh-refresh').addEventListener('click', refreshGitHubStatus);
    document.getElementById('btn-gh-push').addEventListener('click', async () => {
        const out = document.getElementById('gh-push-out');
        out.innerText = '⏳ Commit & Push verso GitHub...';
        const msg = document.getElementById('gh-commit-msg').value.trim();
        const res = await fetch('/api/github/push', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg }),
        }).then(r => r.json());
        out.innerText = `${res.commit_out || ''}\n${res.push_out || ''}`.trim() || JSON.stringify(res);
        refreshGitHubStatus();
    });

    // =========================================================================
    // CODEX-STYLE MINI & PETS DRAWER
    // =========================================================================
    const petDrawer = document.getElementById('pet-drawer');
    const petBackdrop = document.getElementById('pet-backdrop');
    const openPet = () => { petDrawer.classList.add('open'); petBackdrop.classList.add('open'); };
    const closePet = () => { petDrawer.classList.remove('open'); petBackdrop.classList.remove('open'); };
    document.getElementById('btn-open-pet').addEventListener('click', openPet);
    document.getElementById('btn-close-pet').addEventListener('click', closePet);
    petBackdrop.addEventListener('click', closePet);

    async function pushPetConfig(patch) {
        try {
            await fetch('/api/pet/config', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(patch),
            });
        } catch {}
    }

    async function loadPetConfigUI() {
        try {
            const cfg = await fetch('/api/pet/config').then(r => r.json());
            snake.setSkin(cfg.skin || 'emerald');
            miniPet.setSkin(cfg.skin || 'emerald');
            document.querySelectorAll('.skin-btn').forEach(b => b.classList.toggle('active', b.dataset.skin === cfg.skin));
            document.querySelectorAll('[data-pet-style]').forEach(b => b.classList.toggle('active', b.dataset.petStyle === (cfg.style || 'pixel')));
            document.querySelectorAll('[data-pet-size]').forEach(b => b.classList.toggle('active', b.dataset.petSize === (cfg.size || 'medium')));
            const opPct = Math.round((cfg.opacity ?? 0.96) * 100);
            document.getElementById('pet-opacity').value = opPct;
            document.getElementById('pet-opacity-val').innerText = `${opPct}%`;
            document.getElementById('pet-enabled').checked = !!cfg.enabled;
            document.getElementById('pet-all').checked = cfg.show_on_all !== false;
            document.getElementById('pet-whatsapp').checked = cfg.show_on_whatsapp !== false;
            document.getElementById('pet-spotify').checked = cfg.show_on_spotify !== false;
            document.getElementById('pet-browser').checked = cfg.show_on_browser !== false;
            document.getElementById('pet-vscode').checked = cfg.show_on_vscode !== false;
            document.getElementById('pet-tongue').checked = cfg.animated_tongue !== false;
        } catch {}
    }

    document.querySelectorAll('.skin-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.skin-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            snake.setSkin(btn.dataset.skin);
            miniPet.setSkin(btn.dataset.skin);
            pushPetConfig({ skin: btn.dataset.skin });
        });
    });

    document.querySelectorAll('[data-pet-style]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-pet-style]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            miniPet.setStyle(btn.dataset.petStyle);
            pushPetConfig({ style: btn.dataset.petStyle });
        });
    });

    document.querySelectorAll('[data-pet-size]').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('[data-pet-size]').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            pushPetConfig({ size: btn.dataset.petSize });
        });
    });

    document.getElementById('pet-opacity').addEventListener('input', e => {
        const val = Number(e.target.value);
        document.getElementById('pet-opacity-val').innerText = `${val}%`;
        pushPetConfig({ opacity: val / 100 });
    });

    const toggleMap = {
        'pet-enabled': 'enabled',
        'pet-all': 'show_on_all',
        'pet-whatsapp': 'show_on_whatsapp',
        'pet-spotify': 'show_on_spotify',
        'pet-browser': 'show_on_browser',
        'pet-tongue': 'animated_tongue',
    };
    Object.entries(toggleMap).forEach(([elId, cfgKey]) => {
        document.getElementById(elId).addEventListener('change', e => {
            pushPetConfig({ [cfgKey]: e.target.checked });
        });
    });
    document.getElementById('pet-vscode').addEventListener('change', e => {
        pushPetConfig({ show_on_vscode: e.target.checked, show_on_obsidian: e.target.checked });
    });

    document.getElementById('btn-pet-wave').addEventListener('click', () => {
        fetch('/api/pet/action', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'wave' }) });
    });
    document.getElementById('btn-pet-center').addEventListener('click', () => {
        fetch('/api/pet/action', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ action: 'recenter' }) });
    });

    // =========================================================================
    // TELEMETRY STARTUP
    // =========================================================================
    async function refreshTelemetry() {
        try {
            const [bs, sys] = await Promise.all([
                fetch('/api/brain/stats').then(r => r.json()),
                fetch('/api/system/status').then(r => r.json()),
            ]);
            if (bs.available) {
                document.getElementById('txt-brain').innerText = `Brain ${bs.total_notes}n · ${bs.total_links}l`;
                document.getElementById('dock-brain-stat').innerText = `${bs.total_notes} Note · ${bs.total_links} Link`;
            }
            document.getElementById('txt-freellm').innerText = sys.freellm_online ? `FreeLLM (${sys.ready_models})` : 'FreeLLM Offline';
            document.getElementById('dot-freellm').classList.toggle('warn', !sys.freellm_online);
        } catch {}
    }

    addLog('MAMBA OS v2.0 inizializzato.', 'info');
    addLog('Voce Neurale Edge-TTS pronta con coda non-bloccante.', 'info');
    refreshTelemetry();
    refreshGitHubStatus();
    loadPetConfigUI();
});
