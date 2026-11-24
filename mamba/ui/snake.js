/**
 * mamba/ui/snake.js - Retro-Cyber Pixel-Art Mamba Snake Engine (60 FPS)
 *
 * Modalità:
 * - 'idle'     : Cobra Pixel frontale con respiro, blink e lingua biforcuta pixelata
 * - 'thinking' : Serpente pixelato multi-segmento che STRISCIA VELOCEMENTE da sinistra a destra (L -> R)
 *                con scia neon e scintille ogni volta che riceve/scrive un prompt!
 * - 'speaking' : Cobra Pixel frontale reattivo al volume audio reale (VoiceMouth AnalyserNode)
 */

const SNAKE_SKINS = {
    emerald: { primary: '#00ff88', mid: '#059669', dark: '#042e1d', eye: '#eafff5', pupil: '#020b06', tongue: '#00ffaa', glow: '#00ff88' },
    cyber:   { primary: '#c77dff', mid: '#7b2cbf', dark: '#240046', eye: '#f3e8ff', pupil: '#10002b', tongue: '#ff5400', glow: '#c77dff' },
    golden:  { primary: '#ffb703', mid: '#d97706', dark: '#3d2600', eye: '#fef9c3', pupil: '#1a1000', tongue: '#ff0055', glow: '#ffb703' },
    crimson: { primary: '#ff2a6d', mid: '#be123c', dark: '#3a0014', eye: '#ffe4e6', pupil: '#1a0009', tongue: '#ffbe0b', glow: '#ff2a6d' },
    mecha:   { primary: '#00f0ff', mid: '#0284c7', dark: '#002b36', eye: '#e0f2fe', pupil: '#001015', tongue: '#ff007f', glow: '#00f0ff' },
};

// Sprite 16x16 Pixel-Art del Cobra Frontale
const PIXEL_COBRA = [
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

// Testa pixelata orientata a DESTRA (9x7) per lo slither veloce L -> R
const PIXEL_HEAD_RIGHT = [
    "033330000",
    "322223300",
    "324522230",
    "322222233",
    "322112230",
    "033113300",
    "000330000",
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

        // Parametri scorrimento rapido L -> R durante 'thinking'
        this.slitherX = -160;
        this.slitherSpeed = 540; // px/sec rapido ed energico
        this.sparks = [];

        // Particelle pixel ambiente
        this.particles = Array.from({ length: 32 }, () => ({
            x: Math.random(),
            y: Math.random(),
            vx: (Math.random() - 0.5) * 0.04,
            vy: (Math.random() - 0.5) * 0.04,
            size: Math.random() > 0.5 ? 3 : 2,
            alpha: Math.random() * 0.45 + 0.15,
        }));

        this.resize();
        window.addEventListener('resize', () => this.resize());
        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    resize() {
        const parent = this.canvas.parentElement;
        this.width = parent ? parent.clientWidth : 520;
        this.height = parent ? (parent.clientHeight || 260) : 260;
        const dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.canvas.width = Math.floor(this.width * dpr);
        this.canvas.height = Math.floor(this.height * dpr);
        this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        this.ctx.imageSmoothingEnabled = false;
    }

    setState(state, audioLevel = 0) {
        if (state === 'thinking' && this.state !== 'thinking') {
            this.slitherX = -40;
            this.sparks = [];
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

    _snap(v, step = 4) {
        return Math.round(v / step) * step;
    }

    animate(ts) {
        const dt = this.lastTs ? Math.min(0.05, (ts - this.lastTs) * 0.001) : 0.016;
        this.lastTs = ts;
        this.time = ts * 0.001;

        const ctx = this.ctx;
        ctx.clearRect(0, 0, this.width, this.height);

        this._drawPixelGridBackdrop();
        this._drawAmbientPixels(dt);

        if (this.state === 'thinking') {
            this._drawFastSlitherLR(dt);
        } else {
            this._drawFrontPixelCobra();
        }

        requestAnimationFrame(this.animate);
    }

    _drawPixelGridBackdrop() {
        const ctx = this.ctx;
        const cx = this.width * 0.5;
        const cy = this.height * 0.5;
        const grad = ctx.createRadialGradient(cx, cy, 8, cx, cy, Math.max(this.width, this.height) * 0.45);
        grad.addColorStop(0, `${this.skin.primary}1a`);
        grad.addColorStop(1, 'rgba(0,0,0,0)');
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, this.width, this.height);
    }

    _drawAmbientPixels(dt) {
        const ctx = this.ctx;
        ctx.save();
        for (const p of this.particles) {
            p.x += p.vx * dt;
            p.y += p.vy * dt;
            if (p.x < 0) p.x = 1;
            if (p.x > 1) p.x = 0;
            if (p.y < 0) p.y = 1;
            if (p.y > 1) p.y = 0;
            ctx.fillStyle = this.skin.primary;
            ctx.globalAlpha = p.alpha;
            ctx.fillRect(this._snap(p.x * this.width, 3), this._snap(p.y * this.height, 3), p.size, p.size);
        }
        ctx.restore();
    }

    /**
     * Animazione richiesta dall'utente:
     * Serpente pixelato che striscia velocemente da SINISTRA verso DESTRA durante il prompt!
     */
    _drawFastSlitherLR(dt) {
        const ctx = this.ctx;
        const px = 5;
        const segCount = 24;
        const spacing = 14;
        const cy = this.height * 0.5;

        this.slitherX += this.slitherSpeed * dt;
        const tailMargin = segCount * spacing + 80;
        if (this.slitherX - tailMargin > this.width) {
            this.slitherX = -50;
        }

        // Linee di velocità orizzontali pixelate
        ctx.save();
        ctx.fillStyle = this.skin.primary;
        for (let l = 0; l < 7; l++) {
            const ly = this._snap(cy + (l - 3) * 20 + Math.sin(l * 2.3) * 6, px);
            const lx = ((this.slitherX * 1.4 + l * 110) % (this.width + 120)) - 120;
            ctx.globalAlpha = 0.16;
            ctx.fillRect(lx, ly, 42 + (l % 3) * 18, 2);
        }

        // Genera scintille dietro la coda
        if (Math.random() < 0.75) {
            const tailX = this.slitherX - segCount * spacing;
            const tailY = cy + Math.sin(this.time * 18 - segCount * 0.45) * 26;
            this.sparks.push({
                x: tailX,
                y: tailY + (Math.random() - 0.5) * 14,
                vx: -(60 + Math.random() * 110),
                vy: (Math.random() - 0.5) * 40,
                life: 0.45,
            });
        }

        for (let i = this.sparks.length - 1; i >= 0; i--) {
            const sp = this.sparks[i];
            sp.x += sp.vx * dt;
            sp.y += sp.vy * dt;
            sp.life -= dt;
            if (sp.life <= 0) {
                this.sparks.splice(i, 1);
                continue;
            }
            ctx.globalAlpha = sp.life * 1.6;
            ctx.fillStyle = this.skin.primary;
            ctx.fillRect(this._snap(sp.x, px), this._snap(sp.y, px), px, px);
        }

        // Corpo a onda sinusoidale pixelata (coda -> collo)
        ctx.shadowColor = this.skin.glow;
        ctx.shadowBlur = 10;
        for (let i = segCount; i >= 1; i--) {
            const sx = this._snap(this.slitherX - i * spacing, px);
            const wave = Math.sin(this.slitherX * 0.045 - i * 0.42) * 26;
            const sy = this._snap(cy + wave, px);
            const taper = i > segCount - 6 ? (segCount - i + 2) * 2.5 : 16;
            const blockH = Math.max(px, this._snap(taper, px));
            const blockW = px * 3;

            ctx.globalAlpha = Math.max(0.25, 1 - i * 0.025);
            ctx.fillStyle = i % 3 === 0 ? this.skin.dark : this.skin.mid;
            ctx.fillRect(sx, sy - blockH / 2, blockW, blockH);

            // Scaglie neon superiori
            ctx.fillStyle = this.skin.primary;
            ctx.fillRect(sx + px, sy - blockH / 2, px, px);
            if (blockH >= px * 3) {
                ctx.fillRect(sx, sy + blockH / 2 - px, blockW, px);
            }
        }

        // Testa pixelata orientata a destra
        const headWave = Math.sin(this.slitherX * 0.045) * 26;
        const hx = this._snap(this.slitherX - px * 2, px);
        const hy = this._snap(cy + headWave - (7 * px) / 2, px);
        const palette = {
            '1': this.skin.dark,
            '2': this.skin.mid,
            '3': this.skin.primary,
            '4': this.skin.eye,
            '5': this.skin.pupil,
        };
        ctx.globalAlpha = 1;
        for (let r = 0; r < PIXEL_HEAD_RIGHT.length; r++) {
            const row = PIXEL_HEAD_RIGHT[r];
            for (let c = 0; c < row.length; c++) {
                const ch = row[c];
                if (ch === '0') continue;
                ctx.fillStyle = palette[ch];
                ctx.fillRect(hx + c * px, hy + r * px, px, px);
            }
        }

        // Lingua biforcuta veloce verso destra
        const tx = hx + 9 * px;
        const ty = hy + 3 * px;
        const flick = Math.floor(this.time * 24) % 2 === 0 ? px : 0;
        ctx.fillStyle = this.skin.tongue;
        ctx.fillRect(tx, ty, px * 2, px);
        ctx.fillRect(tx + px * 2, ty - px + flick * 0.5, px, px);
        ctx.fillRect(tx + px * 2, ty + px - flick * 0.5, px, px);
        ctx.restore();
    }

    _drawFrontPixelCobra() {
        const ctx = this.ctx;
        const px = Math.max(5, Math.min(9, Math.floor(Math.min(this.width, this.height) / 26)));
        const spriteSize = 16 * px;

        const speakingBoost = this.state === 'speaking' ? (0.4 + this.audioIntensity * 1.4) : 0;
        const bob = this._snap(Math.sin(this.time * (this.state === 'speaking' ? 10 : 2.6)) * (3 + speakingBoost * 5), 2);
        const sway = this._snap(Math.sin(this.time * (this.state === 'speaking' ? 6 : 1.3)) * (this.state === 'speaking' ? 10 : 4), 2);

        const ox = this._snap(this.width * 0.5 + sway - spriteSize * 0.5, px);
        const oy = this._snap(this.height * 0.5 + bob - spriteSize * 0.5 - 6, px);

        const isBlink = Math.sin(this.time * 0.65) > 0.96 && this.state !== 'speaking';
        const palette = {
            '1': this.skin.dark,
            '2': this.skin.mid,
            '3': this.skin.primary,
            '4': isBlink ? this.skin.primary : this.skin.eye,
            '5': isBlink ? this.skin.primary : this.skin.pupil,
        };

        ctx.save();
        // Equalizzatore audio pixelato laterale quando parla
        if (this.state === 'speaking') {
            const bars = 8;
            const amp = Math.max(0.18, this.audioIntensity);
            ctx.fillStyle = this.skin.primary;
            ctx.shadowColor = this.skin.glow;
            ctx.shadowBlur = 10;
            for (let b = 0; b < bars; b++) {
                const hBlocks = Math.max(1, Math.round((0.35 + Math.abs(Math.sin(this.time * 14 + b * 0.9)) * amp * 1.3) * 8));
                const bh = hBlocks * px;
                const yTop = this._snap(this.height * 0.5 - bh * 0.5, px);
                ctx.globalAlpha = 0.55;
                ctx.fillRect(ox - (b + 3) * (px + 2), yTop, px, bh);
                ctx.fillRect(ox + spriteSize + (b + 2) * (px + 2), yTop, px, bh);
            }
            ctx.globalAlpha = 1;
        }

        ctx.shadowColor = this.skin.glow;
        ctx.shadowBlur = this.state === 'speaking' ? 18 : 10;

        for (let r = 0; r < PIXEL_COBRA.length; r++) {
            const row = PIXEL_COBRA[r];
            for (let c = 0; c < row.length; c++) {
                const ch = row[c];
                if (ch === '0') continue;
                ctx.fillStyle = palette[ch];
                ctx.fillRect(ox + c * px, oy + r * px, px, px);
            }
        }

        // Lingua biforcuta pixelata
        const cycle = this.time % 3.2;
        if ((cycle > 0.4 && cycle < 1.2) || this.state === 'speaking') {
            const tx = ox + 7.5 * px;
            const ty = oy + 15 * px;
            const flick = Math.floor(this.time * 18) % 2 === 0 ? px * 0.5 : 0;
            ctx.fillStyle = this.skin.tongue;
            ctx.fillRect(tx - px * 0.5, ty, px, px * 2);
            ctx.fillRect(tx - px * 1.5 + flick, ty + px * 2, px, px);
            ctx.fillRect(tx + px * 0.5 + flick, ty + px * 2, px, px);
        }
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

    setSkin(name) {
        if (SNAKE_SKINS[name]) this.skin = SNAKE_SKINS[name];
    }

    setStyle(st) {
        this.style = st || 'pixel';
    }

    loop() {
        if (!this.canvas) return;
        this.t += 0.05;
        const w = this.canvas.width;
        const h = this.canvas.height;
        const ctx = this.ctx;
        ctx.clearRect(0, 0, w, h);

        const px = 5;
        const sway = Math.round(Math.sin(this.t * (this.hovered ? 5 : 2)) * (this.hovered ? 8 : 3));
        const bob = Math.round(Math.sin(this.t * 2.5) * 2);
        const ox = Math.round(w / 2 - (16 * px) / 2 + sway);
        const oy = Math.round(h / 2 - (16 * px) / 2 + bob);

        const palette = {
            '1': this.skin.dark,
            '2': this.skin.mid,
            '3': this.skin.primary,
            '4': this.skin.eye,
            '5': this.skin.pupil,
        };
        for (let r = 0; r < PIXEL_COBRA.length; r++) {
            for (let c = 0; c < 16; c++) {
                const ch = PIXEL_COBRA[r][c];
                if (ch === '0') continue;
                ctx.fillStyle = palette[ch];
                ctx.fillRect(ox + c * px, oy + r * px, px, px);
            }
        }
        requestAnimationFrame(() => this.loop());
    }
}
