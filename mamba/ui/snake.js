/**
 * mamba/ui/snake.js - Clean Shenron-Style Pixel Serpent Engine (60 FPS)
 * Stile unificato, semplice e pulito:
 * - 'idle'     : Serpente Pixel stile Shenron che ondeggia fluido e rilassato al centro
 * - 'thinking' : Lo stesso Shenron accelera e striscia velocemente da sinistra a destra (L -> R)
 * - 'speaking' : Onda armonica pulita e scaglie illuminate dal volume reale della voce
 */

const SNAKE_SKINS = {
    emerald: { primary: '#00ff88', mid: '#059669', dark: '#042e1d', eye: '#ffffff', pupil: '#02120a', horn: '#a7f3d0', glow: '#00ff88' },
    cyber:   { primary: '#c77dff', mid: '#7b2cbf', dark: '#240046', eye: '#ffffff', pupil: '#10002b', horn: '#e9d5ff', glow: '#c77dff' },
    golden:  { primary: '#ffb703', mid: '#d97706', dark: '#3d2600', eye: '#ffffff', pupil: '#1a1000', horn: '#fef08a', glow: '#ffb703' },
    crimson: { primary: '#ff2a6d', mid: '#be123c', dark: '#3a0014', eye: '#ffffff', pupil: '#1a0009', horn: '#fecdd3', glow: '#ff2a6d' },
    mecha:   { primary: '#00f0ff', mid: '#0284c7', dark: '#002b36', eye: '#ffffff', pupil: '#001015', horn: '#bae6fd', glow: '#00f0ff' },
};

// Testa stile Shenron Pixel (11x8, orientata a destra)
const SHENRON_HEAD = [
    "00300000000",
    "03230000000",
    "00333330000",
    "03222223300",
    "32224522230",
    "03222222233",
    "00321112300",
    "00033333000",
];

// Sprite compatto per anteprima MiniPet
const MINI_PIXEL_COBRA = [
    "0000003333000000",
    "0000332222330000",
    "0003221111223000",
    "0032113333112300",
    "0321322222231230",
    "0321244224421230",
    "0321245225421230",
    "0321222332221230",
    "0032122222212300",
    "0003211331123000",
    "0000321221230000",
    "0003212332123000",
    "0032122112212300",
    "0032112222112300",
    "0003322112233000",
    "0000033333300000",
];

class MambaSnake {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.skinKey = 'emerald';
        this.skin = SNAKE_SKINS.emerald;

        this.state = 'idle'; // 'idle' | 'thinking' | 'speaking'
        this.time = 0;
        this.lastTs = 0;
        this.audioIntensity = 0;
        this.smoothAudio = 0;

        // Posizione testa orizzontale per il dash L->R in thinking
        this.dashHeadX = 0;
        this.phase = 0;

        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    resize() {
        const parent = this.canvas.parentElement;
        this.width = parent ? parent.clientWidth : 560;
        this.height = parent ? (parent.clientHeight || 190) : 190;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.canvas.width = Math.floor(this.width * dpr);
        this.canvas.height = Math.floor(this.height * dpr);
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        this.ctx.imageSmoothingEnabled = false;
    }

    setState(state, audioLevel = 0) {
        if (state === 'thinking' && this.state !== 'thinking') {
            this.dashHeadX = -20;
        }
        this.state = state;
        this.audioIntensity = audioLevel;
    }

    setAudioLevel(level) {
        this.audioIntensity = Math.max(0, Math.min(1, level));
    }

    setSkin(skinName) {
        if (SNAKE_SKINS[skinName]) {
            this.skinKey = skinName;
            this.skin = SNAKE_SKINS[skinName];
        }
    }

    _snap(v, px = 5) {
        return Math.round(v / px) * px;
    }

    animate(ts) {
        const dt = this.lastTs ? Math.min(0.05, (ts - this.lastTs) * 0.001) : 0.016;
        this.lastTs = ts;
        this.time = ts * 0.001;
        this.smoothAudio += (this.audioIntensity - this.smoothAudio) * 0.25;

        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.width, this.height);

        // Soft minimal radial glow
        const cx = this.width * 0.5;
        const cy = this.height * 0.5;
        const bg = ctx.createRadialGradient(cx, cy, 10, cx, cy, this.width * 0.42);
        bg.addColorStop(0, `${this.skin.primary}12`);
        bg.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = bg;
        ctx.fillRect(0, 0, this.width, this.height);

        this._drawShenron(dt);
        requestAnimationFrame(this.animate);
    }

    _drawShenron(dt) {
        const ctx = this.ctx;
        const px = 5;
        const segCount = 26;
        const spacing = 12;
        const cy = this.height * 0.52;

        let headX;
        let waveSpeed;
        let amp;

        if (this.state === 'thinking') {
            // Scorrimento rapido L -> R stile Shenron in volo
            this.dashHeadX += 560 * dt;
            if (this.dashHeadX - segCount * spacing - 60 > this.width) {
                this.dashHeadX = -40;
            }
            headX = this.dashHeadX;
            waveSpeed = 14;
            amp = 24;
            this.phase += waveSpeed * dt;
        } else if (this.state === 'speaking') {
            // Shenron centrato che ondeggia e pulsa con la voce
            headX = this.width * 0.5 + (segCount * spacing) * 0.45 + Math.sin(this.time * 2.2) * 26;
            waveSpeed = 7.5;
            amp = 18 + this.smoothAudio * 18;
            this.phase += waveSpeed * dt;
        } else {
            // Idle pulito: Shenron centrato che fluttua dolcemente
            headX = this.width * 0.5 + (segCount * spacing) * 0.45 + Math.sin(this.time * 1.1) * 18;
            waveSpeed = 3.2;
            amp = 15;
            this.phase += waveSpeed * dt;
        }

        ctx.save();
        // Sottili linee di scia solo in thinking
        if (this.state === 'thinking') {
            ctx.fillStyle = this.skin.primary;
            for (let l = 0; l < 4; l++) {
                const ly = this._snap(cy + (l - 1.5) * 24, px);
                const lx = ((headX * 1.3 + l * 130) % (this.width + 100)) - 100;
                ctx.globalAlpha = 0.14;
                ctx.fillRect(lx, ly, 36, 2);
            }
        }

        ctx.shadowColor = this.skin.glow;
        ctx.shadowBlur = this.state === 'speaking' ? (10 + this.smoothAudio * 12) : 8;

        // Disegna segmenti coda -> collo (sinusoide pulita pixelata)
        for (let i = segCount; i >= 1; i--) {
            const sx = this._snap(headX - i * spacing, px);
            const wave = Math.sin(this.phase - i * 0.36) * amp;
            const sy = this._snap(cy + wave, px);

            // Rastremazione coda elegante stile drago/serpente
            const ratio = i / segCount;
            const thickness = ratio > 0.72 ? Math.max(1, Math.round((1 - ratio) * 14)) : 3;
            const bh = thickness * px;
            const bw = px * 2;

            ctx.globalAlpha = this.state === 'thinking' ? Math.max(0.35, 1 - ratio * 0.5) : 0.94;
            ctx.fillStyle = i % 2 === 0 ? this.skin.mid : this.skin.dark;
            ctx.fillRect(sx, sy - Math.floor(bh / 2), bw, bh);

            // Cresta dorsale luminosa pulita (Shenron ridge)
            ctx.fillStyle = this.skin.primary;
            ctx.fillRect(sx, sy - Math.floor(bh / 2), px, px);
            if (i % 4 === 0 && thickness >= 3) {
                ctx.fillStyle = this.skin.horn;
                ctx.fillRect(sx, sy - Math.floor(bh / 2) - px, px, px);
            }
        }

        // Testa Shenron pixelata
        const headWave = Math.sin(this.phase) * amp;
        const hx = this._snap(headX - px * 2, px);
        const hy = this._snap(cy + headWave - 4 * px, px);

        const palette = {
            '1': this.skin.dark,
            '2': this.skin.mid,
            '3': this.skin.primary,
            '4': this.skin.eye,
            '5': this.skin.pupil,
        };
        ctx.globalAlpha = 1;
        for (let r = 0; r < SHENRON_HEAD.length; r++) {
            const row = SHENRON_HEAD[r];
            for (let c = 0; c < row.length; c++) {
                const ch = row[c];
                if (ch === '0') continue;
                ctx.fillStyle = palette[ch];
                ctx.fillRect(hx + c * px, hy + r * px, px, px);
            }
        }

        // Baffetti sottili stile Shenron / lingua discreta
        const flick = Math.floor(this.time * (this.state === 'thinking' ? 16 : 6)) % 2 === 0 ? px : 0;
        ctx.fillStyle = this.skin.horn;
        ctx.fillRect(hx + 10 * px, hy + 5 * px + flick * 0.4, px, px);
        ctx.fillRect(hx + 11 * px, hy + 6 * px, px, px);

        ctx.restore();
    }
}

class MiniPetPreview {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.ctx.imageSmoothingEnabled = false;
        this.skin = SNAKE_SKINS.emerald;
        this.style = 'pixel';
        this.t = 0;
        this.hovered = false;
        this.canvas.addEventListener('mouseenter', () => { this.hovered = true; });
        this.canvas.addEventListener('mouseleave', () => { this.hovered = false; });
        requestAnimationFrame(() => this.loop());
    }

    setSkin(name) { if (SNAKE_SKINS[name]) this.skin = SNAKE_SKINS[name]; }
    setStyle(st) { this.style = st || 'pixel'; }

    loop() {
        if (!this.canvas) return;
        this.t += 0.05;
        const w = this.canvas.width;
        const h = this.canvas.height;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, w, h);

        const px = 5;
        const sway = Math.round(Math.sin(this.t * (this.hovered ? 5 : 2)) * (this.hovered ? 7 : 3));
        const bob = Math.round(Math.sin(this.t * 2.5) * 2);
        const ox = Math.round(w / 2 - (16 * px) / 2 + sway);
        const oy = Math.round(h / 2 - (16 * px) / 2 + bob);

        const palette = {
            '1': this.skin.dark, '2': this.skin.mid, '3': this.skin.primary,
            '4': this.skin.eye, '5': this.skin.pupil,
        };
        for (let r = 0; r < 16; r++) {
            for (let c = 0; c < 16; c++) {
                const ch = MINI_PIXEL_COBRA[r][c];
                if (ch === '0') continue;
                ctx.fillStyle = palette[ch];
                ctx.fillRect(ox + c * px, oy + r * px, px, px);
            }
        }
        requestAnimationFrame(() => this.loop());
    }
}
