/**
 * galaxy.js - Motore 3D Interattivo 60FPS per la Galaxy View del Secondo Cervello
 * Zero dipendenze esterne: proiezione 3D, fisica a molle sferica, glow additivo,
 * impulsi sinaptici animati, hover neighborhood highlight e inspector live.
 */

const GROUP_CONFIG = {
    all:        { label: "Tutti",     color: "#00ff88" },
    hub:        { label: "Hub",       color: "#ffffff" },
    context:    { label: "Contesto",  color: "#ffb703" },
    project:    { label: "Progetti",  color: "#00ff88" },
    decision:   { label: "Decisioni", color: "#c084fc" },
    daily:      { label: "Diario",    color: "#22d3ee" },
    semantic:   { label: "Wiki",      color: "#60a5fa" },
    procedural: { label: "SOP",       color: "#2dd4bf" },
    working:    { label: "Working",   color: "#fb7185" },
    area:       { label: "Aree",      color: "#facc15" },
    resource:   { label: "Risorse",   color: "#818cf8" },
    inbox:      { label: "Inbox",     color: "#fb923c" },
};

class GalaxyBrain {
    constructor() {
        this.canvas = document.getElementById("galaxy-canvas");
        this.ctx = this.canvas.getContext("2d");

        this.nodes = [];
        this.nodeMap = new Map();
        this.edges = [];
        this.adj = new Map();
        this.stars = [];
        this.pulses = [];
        this.glowCache = new Map();

        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.dpr = Math.min(window.devicePixelRatio || 1, 2);

        // Camera & Inertia
        this.rotX = 0.25;
        this.rotY = 0.4;
        this.velX = 0;
        this.velY = 0;
        this.zoom = 1.05;
        this.targetZoom = 1.05;
        this.autoOrbit = true;
        this.showPulses = true;

        // Interaction State
        this.isDragging = false;
        this.dragMoved = false;
        this.lastMouse = { x: 0, y: 0 };
        this.mouse = { x: -9999, y: -9999 };
        this.hoveredNode = null;
        this.selectedNode = null;
        this.activeFilter = "all";
        this.searchTerm = "";

        this._initStars();
        this._bindEvents();
        this._resize();
        this.loadGraph();
        this._loop();
    }

    _initStars() {
        this.stars = Array.from({ length: 240 }, () => ({
            x: (Math.random() - 0.5) * 2.2,
            y: (Math.random() - 0.5) * 2.2,
            z: (Math.random() - 0.5) * 2.2,
            size: Math.random() * 1.4 + 0.3,
            alpha: Math.random() * 0.55 + 0.15,
            twinkle: Math.random() * Math.PI * 2,
        }));
    }

    _getGlowSprite(color) {
        if (this.glowCache.has(color)) return this.glowCache.get(color);
        const s = 64;
        const c = document.createElement("canvas");
        c.width = s;
        c.height = s;
        const gctx = c.getContext("2d");
        const grad = gctx.createRadialGradient(s / 2, s / 2, 1, s / 2, s / 2, s / 2);
        grad.addColorStop(0, "#ffffff");
        grad.addColorStop(0.22, color);
        grad.addColorStop(0.55, this._hexToRgba(color, 0.25));
        grad.addColorStop(1, "rgba(0,0,0,0)");
        gctx.fillStyle = grad;
        gctx.fillRect(0, 0, s, s);
        this.glowCache.set(color, c);
        return c;
    }

    _hexToRgba(hex, a) {
        const clean = hex.replace("#", "");
        const n = parseInt(clean, 16);
        const r = (n >> 16) & 255;
        const g = (n >> 8) & 255;
        const b = n & 255;
        return `rgba(${r},${g},${b},${a})`;
    }

    _resize() {
        this.width = window.innerWidth;
        this.height = window.innerHeight;
        this.dpr = Math.min(window.devicePixelRatio || 1, 2);
        this.canvas.width = Math.floor(this.width * this.dpr);
        this.canvas.height = Math.floor(this.height * this.dpr);
        this.ctx.setTransform(this.dpr, 0, 0, this.dpr, 0, 0);
    }

    async loadGraph() {
        try {
            const resp = await fetch("/api/brain/graph");
            const data = await resp.json();
            this._buildSimulation(data.nodes || [], data.edges || []);
            this._renderFilterBar();
            this._updateStats();
        } catch (err) {
            document.getElementById("stats-pill").innerText = "Errore connessione Server";
        }
    }

    _buildSimulation(rawNodes, rawEdges) {
        const prevPos = new Map(this.nodes.map(n => [n.id, { x: n.x, y: n.y, z: n.z }]));
        const nCount = Math.max(rawNodes.length, 1);
        const goldenAngle = Math.PI * (3 - Math.sqrt(5));

        this.nodes = rawNodes.map((n, i) => {
            const existing = prevPos.get(n.id);
            const y = 1 - (i / Math.max(nCount - 1, 1)) * 2;
            const rAtY = Math.sqrt(Math.max(0, 1 - y * y));
            const theta = goldenAngle * i;
            // Hub vicini al centro luminoso, foglie su orbite più esterne
            const orbitRadius = Math.max(55, 250 - Math.min(n.degree, 24) * 7.5);
            const cfg = GROUP_CONFIG[n.group] || GROUP_CONFIG.all;
            return {
                ...n,
                color: cfg.color,
                x: existing ? existing.x : Math.cos(theta) * rAtY * orbitRadius,
                y: existing ? existing.y : y * orbitRadius,
                z: existing ? existing.z : Math.sin(theta) * rAtY * orbitRadius,
                vx: 0, vy: 0, vz: 0,
                radius: Math.min(13, 3.6 + Math.sqrt(n.degree + 1) * 1.35),
                sx: 0, sy: 0, sz: 0, scale: 1,
            };
        });

        this.nodeMap = new Map(this.nodes.map(n => [n.id, n]));
        this.adj = new Map(this.nodes.map(n => [n.id, new Set()]));
        this.edges = [];

        for (const e of rawEdges) {
            const s = this.nodeMap.get(e.source);
            const t = this.nodeMap.get(e.target);
            if (s && t) {
                this.edges.push({ s, t });
                this.adj.get(s.id).add(t.id);
                this.adj.get(t.id).add(s.id);
            }
        }

        // Pre-settle force layout 90 iterazioni per disposizione pulita istantanea
        for (let iter = 0; iter < 90; iter++) {
            this._stepPhysics(0.72);
        }
        this._spawnPulses();
    }

    _spawnPulses() {
        this.pulses = [];
        const maxPulses = Math.min(36, this.edges.length);
        for (let i = 0; i < maxPulses; i++) {
            const edge = this.edges[Math.floor(Math.random() * this.edges.length)];
            this.pulses.push({
                edge,
                t: Math.random(),
                speed: 0.004 + Math.random() * 0.007,
            });
        }
    }

    _stepPhysics(damping = 0.85) {
        const nodes = this.nodes;
        const len = nodes.length;
        const repulse = 4200;

        for (let i = 0; i < len; i++) {
            const a = nodes[i];
            // Attrazione leggera al centro sferico (più forte per gli hub)
            const centerPull = 0.003 + Math.min(a.degree, 25) * 0.0005;
            a.vx -= a.x * centerPull;
            a.vy -= a.y * centerPull;
            a.vz -= a.z * centerPull;

            for (let j = i + 1; j < len; j++) {
                const b = nodes[j];
                const dx = a.x - b.x;
                const dy = a.y - b.y;
                const dz = a.z - b.z;
                const d2 = dx * dx + dy * dy + dz * dz + 36;
                if (d2 > 140000) continue;
                const f = repulse / (d2 * Math.sqrt(d2));
                const fx = dx * f, fy = dy * f, fz = dz * f;
                a.vx += fx; a.vy += fy; a.vz += fz;
                b.vx -= fx; b.vy -= fy; b.vz -= fz;
            }
        }

        // Molle lungo gli archi [[wikilink]]
        for (const e of this.edges) {
            const dx = e.t.x - e.s.x;
            const dy = e.t.y - e.s.y;
            const dz = e.t.z - e.s.z;
            const dist = Math.sqrt(dx * dx + dy * dy + dz * dz) || 1;
            const targetLen = 115;
            const k = (dist - targetLen) * 0.0032;
            const fx = (dx / dist) * k;
            const fy = (dy / dist) * k;
            const fz = (dz / dist) * k;
            e.s.vx += fx; e.s.vy += fy; e.s.vz += fz;
            e.t.vx -= fx; e.t.vy -= fy; e.t.vz -= fz;
        }

        for (const n of nodes) {
            n.vx *= damping;
            n.vy *= damping;
            n.vz *= damping;
            n.x += n.vx;
            n.y += n.vy;
            n.z += n.vz;
        }
    }

    _nodeMatches(n) {
        if (this.activeFilter !== "all" && n.group !== this.activeFilter) return false;
        if (this.searchTerm) {
            const q = this.searchTerm.toLowerCase();
            const hay = `${n.title} ${n.stem} ${n.summary} ${n.tags.join(" ")}`.toLowerCase();
            return hay.includes(q);
        }
        return true;
    }

    _project(x, y, z) {
        const cosY = Math.cos(this.rotY), sinY = Math.sin(this.rotY);
        const cosX = Math.cos(this.rotX), sinX = Math.sin(this.rotX);

        // Rotate around Y
        const x1 = x * cosY - z * sinY;
        const z1 = z * cosY + x * sinY;
        // Rotate around X
        const y2 = y * cosX - z1 * sinX;
        const z2 = z1 * cosX + y * sinX;

        const fov = 680 * this.zoom;
        const camZ = 620;
        const denom = Math.max(80, camZ + z2);
        const scale = fov / denom;
        return {
            sx: this.width * 0.5 + x1 * scale,
            sy: this.height * 0.5 + y2 * scale,
            sz: z2,
            scale,
        };
    }

    _loop() {
        requestAnimationFrame(() => this._loop());

        if (this.autoOrbit && !this.isDragging) {
            this.rotY += 0.0018;
        }
        if (!this.isDragging) {
            this.rotY += this.velY;
            this.rotX += this.velX;
            this.velY *= 0.92;
            this.velX *= 0.92;
        }
        this.zoom += (this.targetZoom - this.zoom) * 0.12;
        this._stepPhysics(0.82);

        this._render();
    }

    _render() {
        const ctx = this.ctx;
        const w = this.width;
        const h = this.height;
        const now = performance.now() * 0.001;

        ctx.clearRect(0, 0, w, h);

        // 1. Central cosmic nebula halo
        const neb = ctx.createRadialGradient(w * 0.5, h * 0.5, 20, w * 0.5, h * 0.5, Math.max(w, h) * 0.45);
        neb.addColorStop(0, "rgba(0, 255, 136, 0.07)");
        neb.addColorStop(0.45, "rgba(34, 211, 238, 0.035)");
        neb.addColorStop(1, "rgba(0, 0, 0, 0)");
        ctx.fillStyle = neb;
        ctx.fillRect(0, 0, w, h);

        // 2. Background Deep Starfield
        for (const st of this.stars) {
            const p = this._project(st.x * 520, st.y * 520, st.z * 520);
            const alpha = st.alpha * (0.65 + 0.35 * Math.sin(now * 1.4 + st.twinkle));
            ctx.fillStyle = `rgba(190, 235, 255, ${alpha.toFixed(3)})`;
            ctx.beginPath();
            ctx.arc(p.sx, p.sy, st.size, 0, Math.PI * 2);
            ctx.fill();
        }

        // 3. Project all nodes
        for (const n of this.nodes) {
            const p = this._project(n.x, n.y, n.z);
            n.sx = p.sx;
            n.sy = p.sy;
            n.sz = p.sz;
            n.scale = p.scale;
        }

        // Hover hit-test
        if (!this.isDragging) {
            let best = null;
            let bestDist = 24;
            for (const n of this.nodes) {
                if (!this._nodeMatches(n)) continue;
                const d = Math.hypot(n.sx - this.mouse.x, n.sy - this.mouse.y);
                const hitR = Math.max(12, n.radius * n.scale + 7);
                if (d < hitR && d < bestDist) {
                    bestDist = d;
                    best = n;
                }
            }
            if (best !== this.hoveredNode) {
                this.hoveredNode = best;
                this._updateTooltip();
                this.canvas.style.cursor = best ? "pointer" : (this.isDragging ? "grabbing" : "grab");
            } else if (best) {
                this._moveTooltip();
            }
        }

        const focusNode = this.hoveredNode || this.selectedNode;
        const focusNeighbors = focusNode ? this.adj.get(focusNode.id) : null;

        // 4. Draw Synaptic Edges
        ctx.save();
        ctx.globalCompositeOperation = "lighter";
        for (const e of this.edges) {
            const sMatch = this._nodeMatches(e.s);
            const tMatch = this._nodeMatches(e.t);
            if (!sMatch && !tMatch) continue;

            const isHighlighted = focusNode && (e.s === focusNode || e.t === focusNode);
            let alpha = (sMatch && tMatch) ? 0.14 : 0.04;
            let lineW = 0.8;

            if (focusNode) {
                alpha = isHighlighted ? 0.58 : 0.035;
                lineW = isHighlighted ? 1.7 : 0.6;
            }

            const grad = ctx.createLinearGradient(e.s.sx, e.s.sy, e.t.sx, e.t.sy);
            grad.addColorStop(0, this._hexToRgba(e.s.color, alpha));
            grad.addColorStop(1, this._hexToRgba(e.t.color, alpha));
            ctx.strokeStyle = grad;
            ctx.lineWidth = lineW;
            ctx.beginPath();
            ctx.moveTo(e.s.sx, e.s.sy);
            ctx.lineTo(e.t.sx, e.t.sy);
            ctx.stroke();
        }

        // 5. Traveling Neural Pulses
        if (this.showPulses) {
            for (const p of this.pulses) {
                p.t += p.speed;
                if (p.t >= 1) p.t = 0;
                const s = p.edge.s, t = p.edge.t;
                if (!this._nodeMatches(s) || !this._nodeMatches(t)) continue;
                if (focusNode && s !== focusNode && t !== focusNode) continue;
                const px = s.sx + (t.sx - s.sx) * p.t;
                const py = s.sy + (t.sy - s.sy) * p.t;
                ctx.fillStyle = "rgba(255, 255, 255, 0.85)";
                ctx.beginPath();
                ctx.arc(px, py, 1.8, 0, Math.PI * 2);
                ctx.fill();
            }
        }
        ctx.restore();

        // 6. Depth-Sort Nodes (back to front) & Draw Luminous Stars + Labels
        const sorted = [...this.nodes].sort((a, b) => b.sz - a.sz);

        for (const n of sorted) {
            const matched = this._nodeMatches(n);
            const isFocus = n === focusNode;
            const isNeighbor = focusNeighbors ? focusNeighbors.has(n.id) : false;

            let alpha = matched ? 1.0 : 0.10;
            if (focusNode && matched) {
                alpha = (isFocus || isNeighbor) ? 1.0 : 0.22;
            }

            const r = Math.max(2.2, n.radius * Math.min(1.8, Math.max(0.45, n.scale)));
            const glowSize = r * (isFocus ? 7.2 : (isNeighbor ? 5.6 : 4.5));

            ctx.save();
            ctx.globalAlpha = alpha;
            ctx.globalCompositeOperation = "lighter";
            const sprite = this._getGlowSprite(n.color);
            ctx.drawImage(sprite, n.sx - glowSize / 2, n.sy - glowSize / 2, glowSize, glowSize);

            if (isFocus) {
                ctx.strokeStyle = "#ffffff";
                ctx.lineWidth = 1.6;
                ctx.beginPath();
                ctx.arc(n.sx, n.sy, r + 5, 0, Math.PI * 2);
                ctx.stroke();
            }
            ctx.restore();

            // Label rendering: hubs, searched, hovered, neighbors, or front nodes
            const showLabel =
                matched && (
                    isFocus ||
                    isNeighbor ||
                    this.searchTerm.length > 0 ||
                    n.degree >= 12 ||
                    (n.sz < 50 && n.scale > 0.85)
                );

            if (showLabel) {
                const label = n.stem;
                ctx.save();
                ctx.globalAlpha = isFocus ? 1.0 : (isNeighbor ? 0.95 : Math.min(0.88, alpha * 0.78));
                ctx.font = isFocus ? "700 12px 'Segoe UI', sans-serif" : "600 10.5px 'Segoe UI', sans-serif";
                const tx = n.sx + r + 6;
                const ty = n.sy + 3.5;

                if (isFocus || label === "CHANGELOG" || n.degree >= 22) {
                    const tw = ctx.measureText(label).width;
                    ctx.fillStyle = "rgba(6, 15, 24, 0.82)";
                    ctx.strokeStyle = this._hexToRgba(n.color, 0.55);
                    ctx.lineWidth = 1;
                    ctx.beginPath();
                    ctx.roundRect(tx - 5, ty - 11, tw + 10, 16, 5);
                    ctx.fill();
                    ctx.stroke();
                }

                ctx.fillStyle = isFocus ? "#ffffff" : "#d8eef5";
                ctx.fillText(label, tx, ty);
                ctx.restore();
            }
        }
    }

    _updateStats() {
        const pill = document.getElementById("stats-pill");
        pill.innerHTML = `<b>${this.nodes.length}</b> stelle · <b>${this.edges.length}</b> sinapsi`;
    }

    _renderFilterBar() {
        const bar = document.getElementById("filter-bar");
        const presentGroups = new Set(this.nodes.map(n => n.group));
        const keys = ["all", ...Object.keys(GROUP_CONFIG).filter(k => k !== "all" && presentGroups.has(k))];

        bar.innerHTML = keys.map(k => {
            const cfg = GROUP_CONFIG[k];
            const active = this.activeFilter === k ? "active" : "";
            return `<button class="filter-pill ${active}" data-group="${k}" style="--pill-color:${cfg.color}">
                <span class="dot"></span>${cfg.label}
            </button>`;
        }).join("");

        bar.querySelectorAll(".filter-pill").forEach(btn => {
            btn.addEventListener("click", () => {
                this.activeFilter = btn.dataset.group;
                bar.querySelectorAll(".filter-pill").forEach(b => b.classList.remove("active"));
                btn.classList.add("active");
            });
        });
    }

    _updateTooltip() {
        const tt = document.getElementById("tooltip");
        if (!this.hoveredNode) {
            tt.classList.remove("visible");
            return;
        }
        const n = this.hoveredNode;
        document.getElementById("tt-title").innerText = n.title;
        document.getElementById("tt-meta").innerText = `${(GROUP_CONFIG[n.group]?.label || n.group).toUpperCase()} · ${n.in_links} in / ${n.out_links} out`;
        document.getElementById("tt-sum").innerText = n.summary || n.id;
        tt.classList.add("visible");
        this._moveTooltip();
    }

    _moveTooltip() {
        const tt = document.getElementById("tooltip");
        const x = Math.min(this.width - 310, this.mouse.x + 16);
        const y = Math.min(this.height - 110, this.mouse.y + 16);
        tt.style.left = `${x}px`;
        tt.style.top = `${y}px`;
    }

    async selectNode(node) {
        if (!node) return;
        this.selectedNode = node;
        this.autoOrbit = false;
        document.getElementById("btn-orbit").classList.remove("active");
        document.getElementById("btn-orbit").innerText = "⏸ Orbita";

        // Ruota dolcemente verso il nodo
        const targetRotY = Math.atan2(-node.x, node.z);
        this.velY = (targetRotY - this.rotY) * 0.08;

        const insp = document.getElementById("inspector");
        insp.classList.add("open");
        document.getElementById("insp-title").innerText = node.title;
        document.getElementById("insp-path").innerText = node.id;

        const obsUrl = `obsidian://open?vault=ObsidianVault&file=${encodeURIComponent(node.id)}`;
        document.getElementById("insp-obsidian-btn").href = obsUrl;

        document.getElementById("insp-body").innerHTML = "<p style='color:#7f9bb0'>Caricamento contenuto...</p>";

        try {
            const resp = await fetch(`/api/brain/note?path=${encodeURIComponent(node.id)}`);
            const data = await resp.json();
            document.getElementById("insp-body").innerHTML = this._renderMarkdownLite(data.body || "");

            document.querySelectorAll("#insp-body .wikilink-chip").forEach(chip => {
                chip.addEventListener("click", () => this._jumpToStem(chip.dataset.target));
            });

            const nbBox = document.getElementById("insp-neighbors");
            const neighbors = Array.from(this.adj.get(node.id) || [])
                .map(id => this.nodeMap.get(id))
                .filter(Boolean);
            nbBox.innerHTML = neighbors.map(nb =>
                `<span class="wikilink-chip" data-id="${nb.id}">${nb.stem}</span>`
            ).join("") || "<span style='font-size:11px;color:#7f9bb0'>Nessun collegamento</span>";

            nbBox.querySelectorAll(".wikilink-chip").forEach(ch => {
                ch.addEventListener("click", () => this.selectNode(this.nodeMap.get(ch.dataset.id)));
            });
        } catch (err) {
            document.getElementById("insp-body").innerText = "Errore caricamento nota.";
        }
    }

    _jumpToStem(target) {
        const clean = target.split("|")[0].split("#")[0].trim().toLowerCase();
        const found = this.nodes.find(n =>
            n.id.toLowerCase() === clean ||
            n.id.toLowerCase() === `${clean}.md` ||
            n.stem.toLowerCase() === clean.split("/").pop()
        );
        if (found) this.selectNode(found);
    }

    _renderMarkdownLite(md) {
        let html = md
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");
        html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
        html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
        html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");
        html = html.replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>");
        html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
        html = html.replace(/\[\[([^\]]+)\]\]/g, (_, inner) => {
            const [target, alias] = inner.split("|");
            return `<span class="wikilink-chip" data-target="${target}">${alias || target}</span>`;
        });
        html = html.replace(/^- (.+)$/gm, "<li>$1</li>");
        html = html.replace(/\n\n/g, "<br><br>");
        return html;
    }

    _bindEvents() {
        window.addEventListener("resize", () => this._resize());

        this.canvas.addEventListener("mousedown", e => {
            this.isDragging = true;
            this.dragMoved = false;
            this.lastMouse = { x: e.clientX, y: e.clientY };
        });

        window.addEventListener("mousemove", e => {
            this.mouse = { x: e.clientX, y: e.clientY };
            if (!this.isDragging) return;
            const dx = e.clientX - this.lastMouse.x;
            const dy = e.clientY - this.lastMouse.y;
            if (Math.hypot(dx, dy) > 3) this.dragMoved = true;
            this.rotY += dx * 0.0065;
            this.rotX = Math.max(-1.4, Math.min(1.4, this.rotX + dy * 0.0065));
            this.velY = dx * 0.0022;
            this.velX = dy * 0.0022;
            this.lastMouse = { x: e.clientX, y: e.clientY };
        });

        window.addEventListener("mouseup", () => {
            if (this.isDragging && !this.dragMoved && this.hoveredNode) {
                this.selectNode(this.hoveredNode);
            }
            this.isDragging = false;
        });

        this.canvas.addEventListener("wheel", e => {
            e.preventDefault();
            const factor = e.deltaY > 0 ? 0.90 : 1.11;
            this.targetZoom = Math.max(0.42, Math.min(2.6, this.targetZoom * factor));
        }, { passive: false });

        document.getElementById("search-box").addEventListener("input", e => {
            this.searchTerm = e.target.value.trim();
        });

        const btnOrbit = document.getElementById("btn-orbit");
        btnOrbit.addEventListener("click", () => {
            this.autoOrbit = !this.autoOrbit;
            btnOrbit.classList.toggle("active", this.autoOrbit);
            btnOrbit.innerText = this.autoOrbit ? "▶ Orbita" : "⏸ Orbita";
        });

        const btnPulses = document.getElementById("btn-pulses");
        btnPulses.addEventListener("click", () => {
            this.showPulses = !this.showPulses;
            btnPulses.classList.toggle("active", this.showPulses);
        });

        document.getElementById("btn-reset").addEventListener("click", () => {
            this.targetZoom = 1.05;
            this.rotX = 0.25;
            this.selectedNode = null;
            document.getElementById("inspector").classList.remove("open");
        });

        document.getElementById("insp-close").addEventListener("click", () => {
            document.getElementById("inspector").classList.remove("open");
            this.selectedNode = null;
        });

        document.getElementById("insp-focus-btn").addEventListener("click", () => {
            if (!this.selectedNode) return;
            this.targetZoom = 1.55;
        });

        // Quick Capture Modal
        const modal = document.getElementById("capture-modal");
        const txt = document.getElementById("capture-text");
        document.getElementById("btn-capture").addEventListener("click", () => {
            modal.classList.add("open");
            txt.focus();
        });
        document.getElementById("capture-cancel").addEventListener("click", () => {
            modal.classList.remove("open");
        });
        document.getElementById("capture-save").addEventListener("click", async () => {
            const val = txt.value.trim();
            if (!val) return;
            await fetch("/api/command", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ prompt: `Salva nel cervello: ${val}` }),
            });
            txt.value = "";
            modal.classList.remove("open");
            await this.loadGraph();
        });
    }
}

document.addEventListener("DOMContentLoaded", () => {
    window.galaxyBrain = new GalaxyBrain();
});
