/**
 * mamba/ui/snake.js - Holographic Front-Facing Emerald Viper (Canvas 60fps)
 * 
 * Caratteristiche:
 * - Serpente frontale (Cobra/Mamba) con cappuccio espanso e scaglie olografiche smeraldo (#00ff88)
 * - Occhi penetranti con fessure verticali e bagliore neon
 * - Lingua biforcuta che esce ed entra ritmicamente (idle flick)
 * - Oscillazione fluida da destra a sinistra durante la parola (Speaking sway)
 * - Respiro lento e particelle olografiche reattive
 */

const SNAKE_SKINS = {
    emerald: { primary: '#00ff88', dark: '#042e1d', body: '#07482e', eye: '#00ff88', pupil: '#020b06', tongue: '#00ffaa', glow: '#00ff88' },
    cyber:   { primary: '#c77dff', dark: '#240046', body: '#3c096c', eye: '#e0aaff', pupil: '#10002b', tongue: '#ff5400', glow: '#c77dff' },
    golden:  { primary: '#ffb703', dark: '#3d2600', body: '#5a3a00', eye: '#ffe066', pupil: '#1a1000', tongue: '#ff0055', glow: '#ffb703' },
    crimson: { primary: '#ff0055', dark: '#3a0014', body: '#5c0022', eye: '#ff5488', pupil: '#1a0009', tongue: '#ffbe0b', glow: '#ff0055' },
    mecha:   { primary: '#00f0ff', dark: '#002b36', body: '#003b46', eye: '#00f0ff', pupil: '#001015', tongue: '#ff007f', glow: '#00f0ff' }
};

class MambaSnake {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.skinKey = 'emerald';
        this.skin = SNAKE_SKINS.emerald;
        this.resize();
        window.addEventListener('resize', () => this.resize());

        this.state = 'idle'; // 'idle', 'thinking', 'speaking'
        this.time = 0;
        
        // Parametri animazione lingua
        this.tongueFlick = 0;
        this.lastTongueTime = 0;
        this.isTongueOut = false;

        // Onde audio
        this.audioIntensity = 0;

        // Particelle attorno al serpente
        this.particles = [];
        for (let i = 0; i < 40; i++) {
            this.particles.push({
                x: (Math.random() - 0.5) * 300,
                y: (Math.random() - 0.5) * 300,
                vx: (Math.random() - 0.5) * 0.8,
                vy: (Math.random() - 0.5) * 0.8,
                size: Math.random() * 2 + 1,
                alpha: Math.random() * 0.7 + 0.2
            });
        }

        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    resize() {
        this.width = this.canvas.parentElement.clientWidth;
        this.height = this.canvas.parentElement.clientHeight || 340;
        this.canvas.width = this.width * window.devicePixelRatio;
        this.canvas.height = this.height * window.devicePixelRatio;
        this.ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }

    setState(state, audioLevel = 0) {
        this.state = state;
        this.audioIntensity = audioLevel;
    }

    setSkin(skinName) {
        if (SNAKE_SKINS[skinName]) {
            this.skinKey = skinName;
            this.skin = SNAKE_SKINS[skinName];
        }
    }

    animate(timestamp) {
        this.time = timestamp * 0.001;
        this.ctx.clearRect(0, 0, this.width, this.height);

        const cx = this.width / 2;
        const cy = this.height / 2 + 15;

        // 1. Gestione movimento laterale (Sway)
        let swayX = 0;
        let headTilt = 0;
        let breathe = Math.sin(this.time * 2) * 4;

        if (this.state === 'speaking') {
            // Oscillazione fluida da destra a sinistra quando parla
            swayX = Math.sin(this.time * 4) * 35;
            headTilt = Math.cos(this.time * 4) * 0.08;
            breathe = Math.sin(this.time * 8) * 8;
        } else if (this.state === 'thinking') {
            swayX = Math.sin(this.time * 6) * 15;
            headTilt = Math.sin(this.time * 3) * 0.05;
        } else {
            // Idle lento e ipnotico
            swayX = Math.sin(this.time * 1.2) * 8;
            headTilt = Math.sin(this.time * 1.2) * 0.02;
        }

        // 2. Gestione Lingua Biforcuta (flick ogni 3.5 secondi)
        const cycle = (this.time % 3.5);
        if (cycle > 0.5 && cycle < 1.3) {
            this.isTongueOut = true;
            // Guizzo rapido
            this.tongueFlick = Math.sin(this.time * 28);
        } else {
            this.isTongueOut = false;
            this.tongueFlick = 0;
        }

        this.ctx.save();
        this.ctx.translate(cx + swayX, cy + breathe);
        this.ctx.rotate(headTilt);

        // 3. Disegna particelle fluttuanti di energia verde
        this.drawParticles();

        // 4. Onde energetiche se sta parlando
        if (this.state === 'speaking' || this.audioIntensity > 0) {
            this.drawEnergyWaves();
        }

        // 5. Corpo & Cappuccio del Cobra frontale
        this.drawHoodAndNeck();

        // 6. Testa e dettagli frontali
        this.drawHead();

        // 7. Lingua biforcuta (se attiva)
        if (this.isTongueOut) {
            this.drawTongue();
        }

        // 8. Occhi fluorescenti smeraldo
        this.drawEyes();

        this.ctx.restore();

        requestAnimationFrame(this.animate);
    }

    drawParticles() {
        this.ctx.save();
        for (let p of this.particles) {
            p.x += p.vx;
            p.y += p.vy;
            if (p.x < -180) p.x = 180;
            if (p.x > 180) p.x = -180;
            if (p.y < -150) p.y = 150;
            if (p.y > 150) p.y = -150;

            this.ctx.fillStyle = this.skin.primary;
            this.ctx.globalAlpha = p.alpha * 0.5;
            this.ctx.shadowColor = this.skin.glow;
            this.ctx.shadowBlur = 8;
            this.ctx.beginPath();
            this.ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            this.ctx.fill();
        }
        this.ctx.restore();
    }

    drawEnergyWaves() {
        this.ctx.save();
        const pulse = (Math.sin(this.time * 10) + 1) * 0.5;
        this.ctx.strokeStyle = this.skin.primary;
        this.ctx.globalAlpha = 0.15 + pulse * 0.25;
        this.ctx.lineWidth = 1.5;
        this.ctx.shadowColor = this.skin.glow;
        this.ctx.shadowBlur = 12;

        for (let r of [110, 135, 160]) {
            this.ctx.beginPath();
            this.ctx.ellipse(0, 10, r + pulse * 10, (r + pulse * 10) * 0.65, 0, 0, Math.PI * 2);
            this.ctx.stroke();
        }
        this.ctx.restore();
    }

    drawHoodAndNeck() {
        const ctx = this.ctx;
        ctx.save();

        const grad = ctx.createLinearGradient(0, -60, 0, 120);
        grad.addColorStop(0, this.skin.dark);
        grad.addColorStop(0.5, this.skin.body);
        grad.addColorStop(1, '#020b06');

        ctx.fillStyle = grad;
        ctx.strokeStyle = this.skin.primary;
        ctx.lineWidth = 2;
        ctx.shadowColor = this.skin.glow;
        ctx.shadowBlur = 15;

        // Silhouette del cappuccio espanso del cobra (frontale simmetrico)
        ctx.beginPath();
        ctx.moveTo(0, -50); // Cima testa
        ctx.bezierCurveTo(45, -45, 105, -20, 110, 25);
        ctx.bezierCurveTo(115, 65, 70, 95, 35, 120);
        ctx.lineTo(-35, 120);
        ctx.bezierCurveTo(-70, 95, -115, 65, -110, 25);
        ctx.bezierCurveTo(-105, -20, -45, -45, 0, -50);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Linee olografiche delle scaglie interne
        ctx.strokeStyle = this.skin.primary;
        ctx.globalAlpha = 0.35;
        ctx.lineWidth = 1;
        ctx.shadowBlur = 4;
        for (let y = -20; y <= 90; y += 18) {
            const spread = Math.sin((y + 20) / 110 * Math.PI) * 75 + 15;
            ctx.beginPath();
            ctx.moveTo(-spread, y);
            ctx.quadraticCurveTo(0, y + 10, spread, y);
            ctx.stroke();
        }

        // Colonna vertebrale centrale
        ctx.globalAlpha = 0.7;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(0, -45);
        ctx.lineTo(0, 120);
        ctx.stroke();

        ctx.restore();
    }

    drawHead() {
        const ctx = this.ctx;
        ctx.save();

        ctx.fillStyle = this.skin.body;
        ctx.strokeStyle = this.skin.primary;
        ctx.lineWidth = 2.5;
        ctx.shadowColor = this.skin.glow;
        ctx.shadowBlur = 20;

        ctx.beginPath();
        ctx.moveTo(0, -65);
        ctx.bezierCurveTo(28, -60, 48, -40, 44, -10);
        ctx.bezierCurveTo(40, 15, 20, 25, 0, 30);
        ctx.bezierCurveTo(-20, 25, -40, 15, -44, -10);
        ctx.bezierCurveTo(-48, -40, -28, -60, 0, -65);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Scaglie fronte
        ctx.strokeStyle = this.skin.primary;
        ctx.globalAlpha = 0.6;
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(0, -65);
        ctx.lineTo(0, -20);
        ctx.stroke();

        // Narici
        ctx.fillStyle = this.skin.primary;
        ctx.globalAlpha = 1.0;
        ctx.shadowBlur = 5;
        ctx.beginPath();
        ctx.ellipse(-6, -55, 2, 4, -0.2, 0, Math.PI * 2);
        ctx.ellipse(6, -55, 2, 4, 0.2, 0, Math.PI * 2);
        ctx.fill();

        // Linea bocca frontale
        ctx.strokeStyle = this.skin.primary;
        ctx.globalAlpha = 0.8;
        ctx.lineWidth = 1.5;
        ctx.beginPath();
        ctx.moveTo(-16, 12);
        ctx.quadraticCurveTo(0, 18, 16, 12);
        ctx.stroke();

        ctx.restore();
    }

    drawEyes() {
        const ctx = this.ctx;
        ctx.save();

        const eyeOffsetX = 24;
        const eyeOffsetY = -30;
        const eyeWidth = 10;
        const eyeHeight = 16;

        ctx.shadowColor = this.skin.glow;
        ctx.shadowBlur = 25;
        ctx.fillStyle = this.skin.eye;

        for (let side of [-1, 1]) {
            const ex = side * eyeOffsetX;
            const ey = eyeOffsetY;

            ctx.beginPath();
            ctx.ellipse(ex, ey, eyeWidth, eyeHeight, side * 0.35, 0, Math.PI * 2);
            ctx.fillStyle = this.skin.eye;
            ctx.fill();

            ctx.beginPath();
            ctx.ellipse(ex, ey, 2.2, eyeHeight * 0.85, side * 0.1, 0, Math.PI * 2);
            ctx.fillStyle = this.skin.pupil;
            ctx.fill();

            ctx.beginPath();
            ctx.arc(ex - side * 2, ey - 4, 1.8, 0, Math.PI * 2);
            ctx.fillStyle = '#ffffff';
            ctx.fill();
        }

        ctx.restore();
    }

    drawTongue() {
        const ctx = this.ctx;
        ctx.save();

        const startY = 16;
        const length = 38 + Math.abs(this.tongueFlick) * 12;
        const forkSpread = 9 + this.tongueFlick * 4;

        ctx.strokeStyle = this.skin.tongue;
        ctx.fillStyle = this.skin.tongue;
        ctx.shadowColor = this.skin.glow;
        ctx.shadowBlur = 10;
        ctx.lineWidth = 2.2;
        ctx.lineCap = 'round';

        ctx.beginPath();
        ctx.moveTo(0, startY);
        ctx.lineTo(this.tongueFlick * 2, startY + length * 0.65);
        ctx.stroke();

        const splitY = startY + length * 0.65;
        const tipY = startY + length;

        ctx.beginPath();
        ctx.moveTo(this.tongueFlick * 2, splitY);
        ctx.lineTo(-forkSpread + this.tongueFlick, tipY);
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(this.tongueFlick * 2, splitY);
        ctx.lineTo(forkSpread + this.tongueFlick, tipY);
        ctx.stroke();

        ctx.restore();
    }
}

/**
 * MiniPetPreview - Canvas interattivo all'interno del drawer delle impostazioni
 */
class MiniPetPreview {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        if (!this.canvas) return;
        this.ctx = this.canvas.getContext('2d');
        this.skinKey = 'emerald';
        this.skin = SNAKE_SKINS.emerald;
        this.time = 0;
        this.isHovered = false;
        this.isClicked = false;

        this.canvas.addEventListener('mouseenter', () => this.isHovered = true);
        this.canvas.addEventListener('mouseleave', () => { this.isHovered = false; this.isClicked = false; });
        this.canvas.addEventListener('mousedown', () => {
            this.isClicked = true;
            setTimeout(() => this.isClicked = false, 600);
        });

        this.animate = this.animate.bind(this);
        requestAnimationFrame(this.animate);
    }

    setSkin(skinName) {
        if (SNAKE_SKINS[skinName]) {
            this.skinKey = skinName;
            this.skin = SNAKE_SKINS[skinName];
        }
    }

    animate(timestamp) {
        this.time = timestamp * 0.001;
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        const cx = this.canvas.width / 2;
        const cy = this.canvas.height / 2 + 5;

        const sway = Math.sin(this.time * (this.isHovered ? 6 : 2)) * (this.isHovered ? 12 : 5);
        const breathe = Math.sin(this.time * 3) * 3;
        const jump = this.isClicked ? -10 : 0;

        this.ctx.save();
        this.ctx.translate(cx + sway, cy + breathe + jump);

        // Cappuccio
        this.ctx.fillStyle = this.skin.dark;
        this.ctx.strokeStyle = this.skin.primary;
        this.ctx.lineWidth = 1.5;
        this.ctx.shadowColor = this.skin.glow;
        this.ctx.shadowBlur = 10;
        this.ctx.beginPath();
        this.ctx.ellipse(0, 0, 36, 42, 0, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.stroke();

        // Testa
        this.ctx.fillStyle = this.skin.body;
        this.ctx.beginPath();
        this.ctx.ellipse(0, -5, 20, 26, 0, 0, Math.PI * 2);
        this.ctx.fill();
        this.ctx.stroke();

        // Lingua se hover o click
        if (this.isHovered || this.isClicked || (this.time % 3.0 > 0.4 && this.time % 3.0 < 1.0)) {
            const flick = Math.sin(this.time * 25) * 3;
            this.ctx.strokeStyle = this.skin.tongue;
            this.ctx.lineWidth = 1.8;
            this.ctx.beginPath();
            this.ctx.moveTo(0, 20);
            this.ctx.lineTo(flick, 36);
            this.ctx.lineTo(-4 + flick, 42);
            this.ctx.moveTo(flick, 36);
            this.ctx.lineTo(4 + flick, 42);
            this.ctx.stroke();
        }

        // Occhi
        for (let s of [-1, 1]) {
            this.ctx.fillStyle = this.skin.eye;
            this.ctx.shadowColor = this.skin.glow;
            this.ctx.shadowBlur = 6;
            this.ctx.beginPath();
            this.ctx.ellipse(s * 9, -8, 4, 6, s * 0.2, 0, Math.PI * 2);
            this.ctx.fill();

            this.ctx.fillStyle = this.skin.pupil;
            this.ctx.beginPath();
            this.ctx.ellipse(s * 9, -8, 1, 5, 0, 0, Math.PI * 2);
            this.ctx.fill();
        }

        this.ctx.restore();
        requestAnimationFrame(this.animate);
    }
}

window.MambaSnake = MambaSnake;
window.MiniPetPreview = MiniPetPreview;
window.SNAKE_SKINS = SNAKE_SKINS;
