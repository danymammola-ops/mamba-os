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

class MambaSnake {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
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

            this.ctx.fillStyle = `rgba(0, 255, 136, ${p.alpha * 0.6})`;
            this.ctx.shadowColor = '#00ff88';
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
        this.ctx.strokeStyle = `rgba(0, 255, 136, ${0.15 + pulse * 0.25})`;
        this.ctx.lineWidth = 1.5;
        this.ctx.shadowColor = '#00ff88';
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

        // Gradiente corpo smeraldo olografico
        const grad = ctx.createLinearGradient(0, -60, 0, 120);
        grad.addColorStop(0, '#042e1d');
        grad.addColorStop(0.5, '#07482e');
        grad.addColorStop(1, '#02180f');

        ctx.fillStyle = grad;
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 2;
        ctx.shadowColor = '#00ff88';
        ctx.shadowBlur = 15;

        // Silhouette del cappuccio espanso del cobra (frontale simmetrico)
        ctx.beginPath();
        ctx.moveTo(0, -50); // Cima testa
        // Lato destro cappuccio
        ctx.bezierCurveTo(45, -45, 105, -20, 110, 25);
        ctx.bezierCurveTo(115, 65, 70, 95, 35, 120);
        ctx.lineTo(-35, 120);
        // Lato sinistro cappuccio
        ctx.bezierCurveTo(-70, 95, -115, 65, -110, 25);
        ctx.bezierCurveTo(-105, -20, -45, -45, 0, -50);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Linee olografiche delle scaglie interne del cappuccio
        ctx.strokeStyle = 'rgba(0, 255, 136, 0.35)';
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
        ctx.strokeStyle = 'rgba(0, 255, 136, 0.7)';
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

        // Sagoma frontale della testa (triangolare affilata mamba)
        ctx.fillStyle = '#062d1c';
        ctx.strokeStyle = '#00ff88';
        ctx.lineWidth = 2.5;
        ctx.shadowColor = '#00ff88';
        ctx.shadowBlur = 20;

        ctx.beginPath();
        ctx.moveTo(0, -65); // Naso frontale
        ctx.bezierCurveTo(28, -60, 48, -40, 44, -10); // Mascella destra
        ctx.bezierCurveTo(40, 15, 20, 25, 0, 30);      // Mento
        ctx.bezierCurveTo(-20, 25, -40, 15, -44, -10); // Mascella sinistra
        ctx.bezierCurveTo(-48, -40, -28, -60, 0, -65);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Piastre e scaglie sulla fronte frontale
        ctx.strokeStyle = 'rgba(0, 255, 136, 0.6)';
        ctx.lineWidth = 1.2;
        ctx.beginPath();
        ctx.moveTo(0, -65);
        ctx.lineTo(0, -20);
        ctx.stroke();

        // Narici
        ctx.fillStyle = '#00ff88';
        ctx.shadowBlur = 5;
        ctx.beginPath();
        ctx.ellipse(-6, -55, 2, 4, -0.2, 0, Math.PI * 2);
        ctx.ellipse(6, -55, 2, 4, 0.2, 0, Math.PI * 2);
        ctx.fill();

        // Linea bocca frontale
        ctx.strokeStyle = 'rgba(0, 255, 136, 0.8)';
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

        // Bagliore esterno occhi
        ctx.shadowColor = '#00ff88';
        ctx.shadowBlur = 25;
        ctx.fillStyle = '#00ff88';

        // Occhio Destro & Sinistro
        for (let side of [-1, 1]) {
            const ex = side * eyeOffsetX;
            const ey = eyeOffsetY;

            // Sclera verde smeraldo brillante
            ctx.beginPath();
            ctx.ellipse(ex, ey, eyeWidth, eyeHeight, side * 0.35, 0, Math.PI * 2);
            ctx.fillStyle = '#00ff88';
            ctx.fill();

            // Pupilla a fessura verticale nera da rettile
            ctx.beginPath();
            ctx.ellipse(ex, ey, 2.2, eyeHeight * 0.85, side * 0.1, 0, Math.PI * 2);
            ctx.fillStyle = '#020b06';
            ctx.fill();

            // Riflesso brillante nell'angolo
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

        // Posizione bocca
        const startY = 16;
        const length = 38 + Math.abs(this.tongueFlick) * 12;
        const forkSpread = 9 + this.tongueFlick * 4;

        ctx.strokeStyle = '#00ffaa';
        ctx.fillStyle = '#00ffaa';
        ctx.shadowColor = '#00ff88';
        ctx.shadowBlur = 10;
        ctx.lineWidth = 2.2;
        ctx.lineCap = 'round';

        // Base della lingua che esce dal mento
        ctx.beginPath();
        ctx.moveTo(0, startY);
        ctx.lineTo(this.tongueFlick * 2, startY + length * 0.65);
        ctx.stroke();

        // Biforcazione sinistra e destra
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

window.MambaSnake = MambaSnake;
