// render.js — All visual rendering: SVG tree, stats, result bar, comparison window.
// Single Responsibility: this file only handles what the user sees on screen.

const NR = 26, VG = 74;

// ─── LOCAL TREE STRUCTURES (used only for demo mode) ─────────────────────────
function LocalNode(v) { this.val = v; this.left = this.right = null; this.height = 1; }

function bstInsert(r, v) {
    if (!r) return new LocalNode(v);
    if (v < r.val) r.left = bstInsert(r.left, v);
    else if (v > r.val) r.right = bstInsert(r.right, v);
    return r;
}

function ht(n)  { return n ? n.height : 0; }
function bf(n)  { return n ? ht(n.left) - ht(n.right) : 0; }
function upH(n) { n.height = 1 + Math.max(ht(n.left), ht(n.right)); }
function rotR(y) { const x = y.left, T = x.right; x.right = y; y.left = T; upH(y); upH(x); return x; }
function rotL(x) { const y = x.right, T = y.left; y.left = x; x.right = T; upH(x); upH(y); return y; }
function bal(n) {
    upH(n);
    const b = bf(n);
    if (b >  1) { if (bf(n.left)  < 0) n.left  = rotL(n.left);  return rotR(n); }
    if (b < -1) { if (bf(n.right) > 0) n.right = rotR(n.right); return rotL(n); }
    return n;
}
function avlInsert(r, v) {
    if (!r) return new LocalNode(v);
    if (v < r.val) r.left = avlInsert(r.left, v);
    else if (v > r.val) r.right = avlInsert(r.right, v);
    else return r;
    return bal(r);
}

// ─── LAYOUT ──────────────────────────────────────────────────────────────────
function treeW(n) {
    if (!n) return 0;
    return Math.max(treeW(n.left) + treeW(n.right), 1);
}

function layout(n, d, l, r, pos) {
    if (!n) return;
    const mid = (l + r) / 2;
    pos[n.val] = { x: mid, y: d * VG + NR + 20 };
    layout(n.left,  d + 1, l,   mid, pos);
    layout(n.right, d + 1, mid, r,   pos);
}

function getLayout(root) {
    const pos = {};
    if (!root) return pos;
    const w = Math.max(treeW(root) * (NR * 2 + 20), 560);
    layout(root, 0, 0, w, pos);
    let minX = Infinity;
    Object.values(pos).forEach(p => { if (p.x < minX) minX = p.x; });
    const off = minX < NR + 8 ? NR + 8 - minX : 0;
    Object.values(pos).forEach(p => p.x += off);
    return pos;
}

function getEdges(n, pos, edges = []) {
    if (!n) return edges;
    if (n.left  && pos[n.val] && pos[n.left.val])  edges.push({ f: pos[n.val], t: pos[n.left.val]  });
    if (n.right && pos[n.val] && pos[n.right.val]) edges.push({ f: pos[n.val], t: pos[n.right.val] });
    getEdges(n.left,  pos, edges);
    getEdges(n.right, pos, edges);
    return edges;
}

// ─── MAIN RENDER ─────────────────────────────────────────────────────────────
function render() {
    const svg   = document.getElementById('tree-svg');
    const empty = document.getElementById('empty-msg');
    const stats = document.getElementById('stats');

    if (!root) {
        svg.style.display   = 'none';
        empty.style.display = 'flex';
        stats.style.display = 'none';
        document.getElementById('result-bar').innerHTML = '';
        return;
    }

    empty.style.display = 'none';
    svg.style.display   = 'block';
    stats.style.display = 'block';

    const pos   = getLayout(root);
    const edges = getEdges(root, pos);
    const vals  = Object.keys(pos);
    const xs    = vals.map(v => pos[v].x);
    const ys    = vals.map(v => pos[v].y);
    const W     = Math.max(...xs) + NR + 24;
    const H     = Math.max(...ys) + NR + 24;

    svg.setAttribute('width',   W);
    svg.setAttribute('height',  H);
    svg.setAttribute('viewBox', `0 0 ${W} ${H}`);

    let html = '';
    edges.forEach(e => {
        html += `<line x1="${e.f.x}" y1="${e.f.y}" x2="${e.t.x}" y2="${e.t.y}"
            stroke="#21262d" stroke-width="2" stroke-linecap="round"/>`;
    });

    vals.forEach(v => {
        const nodeKey = String(v);
        const p = pos[v];
        const isPath = pathNodes.has(v)  || pathNodes.has(nodeKey);
        const isHl   = highlighted.has(v) || highlighted.has(nodeKey);
        const fill   = isPath ? '#bc8cff22' : isHl ? '#58a6ff22' : '#161b22';
        const stroke = isPath ? '#bc8cff'   : isHl ? '#58a6ff'   : '#30363d';
        const sw     = (isPath || isHl) ? 2.5 : 1.5;
        const filter = (isPath || isHl) ? `filter:drop-shadow(0 0 7px ${stroke}66)` : '';
        html += `<g style="${filter}">
            <circle cx="${p.x}" cy="${p.y}" r="${NR}" fill="${fill}" stroke="${stroke}" stroke-width="${sw}"/>
            <text x="${p.x}" y="${p.y + 5}" text-anchor="middle" font-size="13"
                font-weight="700" font-family="IBM Plex Mono,monospace"
                fill="${(isPath || isHl) ? '#fff' : '#c9d1d9'}">${nodeKey}</text>
        </g>`;
    });

    svg.innerHTML = html;
    renderStats();
}

function renderStats() {
    function inorder(n, a = []) { if (!n) return a; inorder(n.left, a); a.push(n.val); inorder(n.right, a); return a; }
    const nodes = inorder(root);
    document.getElementById('s-nodes').textContent  = nodes.length;
    document.getElementById('s-height').textContent = ht(root);
    document.getElementById('s-bf').textContent     = bf(root);

    const isNumeric = nodes.every(n => typeof n === 'number');
    if (isNumeric) {
        document.getElementById('s-min').textContent = Math.min(...nodes);
        document.getElementById('s-max').textContent = Math.max(...nodes);
    } else {
        const sorted = nodes.map(n => String(n)).sort((a, b) => a.localeCompare(b));
        document.getElementById('s-min').textContent = sorted[0] || '—';
        document.getElementById('s-max').textContent = sorted[sorted.length - 1] || '—';
    }
}

// ─── RESULT BAR ──────────────────────────────────────────────────────────────
function showResult(label, arr, isPath) {
    const bar       = document.getElementById('result-bar');
    const pillClass = isPath ? 'result-pill path' : 'result-pill';
    bar.innerHTML   = `<span class="result-label">${label}</span>` +
        arr.map(v => `<span class="${pillClass}">${v}</span>`).join('');
}

// ─── LOG ─────────────────────────────────────────────────────────────────────
function addLog(msg, type) {
    const el  = document.getElementById('log-entries');
    const cls = type === 'ok' ? 'log-ok' : type === 'err' ? 'log-err' : 'log-info';
    el.innerHTML = `<div class="log-entry ${cls}">› ${msg}</div>` + el.innerHTML;
}

// ─── COMPARISON WINDOW ───────────────────────────────────────────────────────
function openComparisonWindow(comparison, properties, loadMode, detectedKey) {
    if (!comparison || !comparison.avl || !comparison.bst) {
        addLog('No hay datos suficientes para comparación AVL/BST.', 'err');
        return;
    }

    const win = window.open('', '_blank', 'width=1300,height=850');
    if (!win) { addLog('El navegador bloqueó la ventana de comparación.', 'err'); return; }

    const avlPayload  = JSON.stringify(comparison.avl).replace(/</g, '\\u003c');
    const bstPayload  = JSON.stringify(comparison.bst).replace(/</g, '\\u003c');
    const propsPayload = JSON.stringify(properties || {}).replace(/</g, '\\u003c');

    const html = `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Comparación AVL vs BST</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; background: #0d1117; color: #c9d1d9; }
        .header { padding: 16px 20px; border-bottom: 1px solid #30363d; }
        .meta { font-size: 13px; color: #8b949e; margin-top: 6px; }
        .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; padding: 12px; }
        .card { border: 1px solid #30363d; border-radius: 8px; background: #161b22; overflow: hidden; }
        .title { padding: 10px 12px; border-bottom: 1px solid #30363d; font-weight: 700; }
        .props { display: flex; gap: 12px; padding: 10px 12px; font-size: 13px; border-bottom: 1px solid #30363d; }
        .prop-item { background: #0d1117; border: 1px solid #30363d; border-radius: 6px; padding: 6px 8px; }
        .canvas { padding: 8px; overflow: auto; }
        svg { width: 100%; min-height: 460px; background: #0d1117; border-radius: 6px; }
    </style>
</head>
<body>
    <div class="header">
        <h2 style="margin:0">Comparación Estructural AVL vs BST</h2>
        <div class="meta">Modo de carga: ${loadMode || 'auto'} | Clave detectada: ${detectedKey || 'auto'}</div>
    </div>
    <div class="grid">
        <div class="card">
            <div class="title">Árbol AVL (principal)</div>
            <div class="props" id="props-avl"></div>
            <div class="canvas"><svg id="svg-avl"></svg></div>
        </div>
        <div class="card">
            <div class="title">Árbol BST</div>
            <div class="props" id="props-bst"></div>
            <div class="canvas"><svg id="svg-bst"></svg></div>
        </div>
    </div>
    <script>
        const avlTree = ${avlPayload};
        const bstTree = ${bstPayload};
        const props   = ${propsPayload};

        function renderProps(id, data) {
            const v = data || {};
            document.getElementById(id).innerHTML =
                '<div class="prop-item">Raíz: '        + (v.root   ?? '—') + '</div>' +
                '<div class="prop-item">Profundidad: ' + (v.depth  ?? 0)   + '</div>' +
                '<div class="prop-item">Hojas: '       + (v.leaves ?? 0)   + '</div>' +
                '<div class="prop-item">Nodos: '       + (v.nodes  ?? 0)   + '</div>';
        }

        function treeWidth(n) { return !n ? 0 : Math.max(treeWidth(n.left) + treeWidth(n.right), 1); }

        function assignPositions(n, d, l, r, path, pos) {
            if (!n) return;
            const mid = (l + r) / 2;
            pos[path] = { x: mid, y: d * 86 + 44, val: n.val };
            assignPositions(n.left,  d+1, l,   mid, path+'L', pos);
            assignPositions(n.right, d+1, mid, r,   path+'R', pos);
        }

        function collectEdges(n, path, pos, edges) {
            if (!n) return;
            const cur = pos[path];
            if (n.left  && pos[path+'L']) edges.push({ from: cur, to: pos[path+'L'] });
            if (n.right && pos[path+'R']) edges.push({ from: cur, to: pos[path+'R'] });
            collectEdges(n.left,  path+'L', pos, edges);
            collectEdges(n.right, path+'R', pos, edges);
        }

        function renderTree(svgId, treeRoot, palette) {
            const svg = document.getElementById(svgId);
            if (!treeRoot) { svg.innerHTML = ''; return; }
            const pos = {};
            assignPositions(treeRoot, 0, 0, Math.max(treeWidth(treeRoot) * 96, 560), 'R', pos);
            const edges = [];
            collectEdges(treeRoot, 'R', pos, edges);
            const keys = Object.keys(pos);
            const maxX = Math.max(...keys.map(k => pos[k].x)) + 44;
            const maxY = Math.max(...keys.map(k => pos[k].y)) + 44;
            svg.setAttribute('viewBox', '0 0 ' + maxX + ' ' + maxY);
            let html = '';
            edges.forEach(e => { html += '<line x1="'+e.from.x+'" y1="'+e.from.y+'" x2="'+e.to.x+'" y2="'+e.to.y+'" stroke="#30363d" stroke-width="2"/>'; });
            keys.forEach(k => {
                const p = pos[k];
                html += '<g><circle cx="'+p.x+'" cy="'+p.y+'" r="26" fill="#0d1117" stroke="'+palette+'" stroke-width="2.2"/>' +
                        '<text x="'+p.x+'" y="'+(p.y+5)+'" text-anchor="middle" fill="#c9d1d9" font-size="12" font-weight="700">'+p.val+'</text></g>';
            });
            svg.innerHTML = html;
        }

        renderProps('props-avl', props.avl || {});
        renderProps('props-bst', props.bst || {});
        renderTree('svg-avl', avlTree, '#58a6ff');
        renderTree('svg-bst', bstTree, '#f2cc60');
    <\/script>
</body>
</html>`;

    win.document.open();
    win.document.write(html);
    win.document.close();
}