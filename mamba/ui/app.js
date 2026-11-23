/**
 * mamba/ui/app.js - Controller Frontend per Mamba OS HUD
 */

document.addEventListener('DOMContentLoaded', () => {
    // 1. Inizializza Serpente Canvas
    const snake = new MambaSnake('snake-canvas');

    const logsContainer = document.getElementById('logs-container');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const responseCard = document.getElementById('response-card');
    const responseText = document.getElementById('response-text');
    const responseLatency = document.getElementById('response-latency');
    const clockDisplay = document.getElementById('clock-display');
    const copyLogsBtn = document.getElementById('copy-logs-btn');
    const clearLogsBtn = document.getElementById('clear-logs-btn');

    // 2. Orologio in tempo reale
    setInterval(() => {
        const now = new Date();
        clockDisplay.innerText = now.toTimeString().split(' ')[0];
    }, 1000);

    // 3. Sistema di Log selezionabili
    function addLog(text, level = 'info') {
        const timeStr = new Date().toTimeString().split(' ')[0];
        const div = document.createElement('div');
        div.className = `log-entry ${level}`;
        div.innerHTML = `<span class="log-time">[${timeStr}]</span><span class="log-text">${text}</span>`;
        logsContainer.appendChild(div);
        logsContainer.scrollTop = logsContainer.scrollHeight;
    }

    // Log iniziali di benvenuto
    addLog('MAMBA OS Neural HUD inizializzato.', 'info');
    addLog('FreeLLMAPI Gateway connesso (300+ modelli a 0 token).', 'info');
    addLog('Safety Gate Verifier: ATTIVO per WhatsApp.', 'info');
    addLog('Squadra Micro-Agenti pronta all\'ascolto.', 'info');

    // Copia e pulizia log
    copyLogsBtn.addEventListener('click', () => {
        const fullText = Array.from(logsContainer.querySelectorAll('.log-entry'))
            .map(e => e.innerText).join('\n');
        navigator.clipboard.writeText(fullText).then(() => {
            addLog('Log copiati negli appunti!', 'warn');
        });
    });

    clearLogsBtn.addEventListener('click', () => {
        logsContainer.innerHTML = '';
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }
        snake.setState('idle');
        fetch('/api/chat/clear', { method: 'POST' }).catch(() => {});
        addLog('Console logs e memoria chat resettate.', 'info');
    });

    // 4. Invio comandi al server backend
    async function sendCommand(prompt) {
        if (!prompt || !prompt.trim()) return;
        const text = prompt.trim();
        userInput.value = '';

        // INTERRUZIONE IMMEDIATA VOCE PRECEDENTE
        if ('speechSynthesis' in window) {
            window.speechSynthesis.cancel();
        }

        addLog(`TU: "${text}"`, 'info');
        snake.setState('thinking');
        responseCard.classList.remove('hidden');
        responseText.innerText = 'Elaborazione in corso con FreeLLMAPI e Micro-Agenti...';
        responseLatency.innerText = '...';

        const t0 = performance.now();

        try {
            const resp = await fetch('/api/command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ prompt: text })
            });
            const data = await resp.json();
            const elapsed = ((performance.now() - t0) / 1000).toFixed(2);

            responseLatency.innerText = `${elapsed}s`;

            if (data.success) {
                responseText.innerText = data.output || 'Azione completata con successo.';
                addLog(`MAMBA: ${data.output}`, 'info');
                addLog(`Rotta: [${data.route.toUpperCase()}] | Tempo: ${elapsed}s | Costo: 0.00€`, 'warn');

                // Serpente entra in modalità speaking mentre risponde
                snake.setState('speaking');
                
                // Se c'è sintesi vocale del browser, parla!
                if ('speechSynthesis' in window) {
                    window.speechSynthesis.cancel(); // Sicurezza extra prima di iniziare
                    const utter = new SpeechSynthesisUtterance(data.output);
                    utter.lang = 'it-IT';
                    utter.rate = 1.05;
                    utter.onend = () => snake.setState('idle');
                    utter.onerror = () => snake.setState('idle');
                    window.speechSynthesis.speak(utter);
                } else {
                    setTimeout(() => snake.setState('idle'), 3500);
                }
            } else {
                responseText.innerText = `Errore: ${data.error}`;
                addLog(`ERRORE: ${data.error}`, 'error');
                snake.setState('idle');
            }
        } catch (err) {
            responseText.innerText = `Errore di rete: ${err.message}`;
            addLog(`ERRORE CONNESSIONE: ${err.message}`, 'error');
            snake.setState('idle');
        }
    }

    sendBtn.addEventListener('click', () => {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        sendCommand(userInput.value);
    });
    userInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            if ('speechSynthesis' in window) window.speechSynthesis.cancel();
            sendCommand(userInput.value);
        }
    });

    // Quick Action Chips
    window.quickSend = function(txt) {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        sendCommand(txt);
    };

    // 5. Riconoscimento Vocale Web Speech API
    let recognition = null;
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRec();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'it-IT';

        recognition.onstart = () => {
            if ('speechSynthesis' in window) {
                window.speechSynthesis.cancel();
            }
            micBtn.classList.add('active');
            addLog('Ascolto microfono avviato...', 'warn');
            snake.setState('thinking');
        };

        recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            addLog(`VOCE RILEVATA: "${transcript}"`, 'info');
            sendCommand(transcript);
        };

        recognition.onerror = (e) => {
            micBtn.classList.remove('active');
            addLog(`Errore microfono: ${e.error}`, 'error');
            snake.setState('idle');
        };

        recognition.onend = () => {
            micBtn.classList.remove('active');
        };

        micBtn.addEventListener('click', () => {
            if (micBtn.classList.contains('active')) {
                recognition.stop();
            } else {
                recognition.start();
            }
        });
    } else {
        micBtn.style.opacity = '0.3';
        micBtn.title = 'Riconoscimento vocale non supportato in questo browser.';
    }

    // ==========================================================================
    // 6. MINI & PETS SETTINGS (DRAWER & PILLOLETTE TOGGLE)
    // ==========================================================================
    const petDrawerBtn = document.getElementById('pet-drawer-btn');
    const petDrawer = document.getElementById('pet-drawer');
    const petDrawerOverlay = document.getElementById('pet-drawer-overlay');
    const drawerCloseBtn = document.getElementById('drawer-close-btn');

    // Inizializza anteprima mini pet
    const miniPet = new MiniPetPreview('mini-pet-preview-canvas');

    function openPetDrawer() {
        petDrawer.classList.add('open');
        petDrawerOverlay.classList.add('open');
        addLog('Impostazioni Mini & Pets aperte.', 'info');
    }

    function closePetDrawer() {
        petDrawer.classList.remove('open');
        petDrawerOverlay.classList.remove('open');
    }

    petDrawerBtn.addEventListener('click', openPetDrawer);
    drawerCloseBtn.addEventListener('click', closePetDrawer);
    petDrawerOverlay.addEventListener('click', closePetDrawer);

    // Selezione Skin / Specie del Serpente
    const skinButtons = document.querySelectorAll('.skin-btn');
    skinButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            skinButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            const skin = btn.getAttribute('data-skin');
            snake.setSkin(skin);
            miniPet.setSkin(skin);
            addLog(`Skin Serpente modificata in: [${skin.toUpperCase()}]`, 'warn');

            // Notifica backend per aggiornare il Desktop Pet fluttuante
            fetch('/api/pet/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ skin: skin })
            }).catch(() => {});
        });
    });

    // Pillolette Switch ON/OFF (Desktop Overlay e App)
    const pillDesktop = document.getElementById('pill-desktop-overlay');
    const pillWhatsApp = document.getElementById('pill-whatsapp');
    const pillSpotify = document.getElementById('pill-spotify');
    const pillBrowser = document.getElementById('pill-browser');
    const pillNotepad = document.getElementById('pill-notepad');
    const pillTongue = document.getElementById('pill-tongue');
    const pillSway = document.getElementById('pill-sway');

    async function syncPillConfig() {
        const cfg = {
            enabled: pillDesktop.checked,
            show_on_whatsapp: pillWhatsApp.checked,
            show_on_spotify: pillSpotify.checked,
            show_on_browser: pillBrowser.checked,
            show_on_notepad: pillNotepad.checked,
            animated_tongue: pillTongue.checked,
            speaking_sway: pillSway.checked
        };
        try {
            await fetch('/api/pet/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(cfg)
            });
        } catch (e) {}
    }

    pillDesktop.addEventListener('change', () => {
        const state = pillDesktop.checked ? 'ATTIVATO' : 'DISATTIVATO';
        addLog(`Floating Desktop Pet: ${state}`, pillDesktop.checked ? 'info' : 'warn');
        syncPillConfig();
    });

    [pillWhatsApp, pillSpotify, pillBrowser, pillNotepad, pillTongue, pillSway].forEach(p => {
        p.addEventListener('change', () => {
            addLog(`Impostazione Pet aggiornata: ${p.id.replace('pill-', '')} -> ${p.checked ? 'ON' : 'OFF'}`, 'info');
            syncPillConfig();
        });
    });
});
