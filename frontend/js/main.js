// main.js — Application logic and user interaction handlers.
// Single Responsibility: orchestrates user actions using api.js and render.js.

// ─── STATE ───────────────────────────────────────────────────────────────────
let root        = null;
let mode        = 'BST';
let highlighted = new Set();
let pathNodes   = new Set();
let activeTrav  = '';

// Tracks whether the flight modal is in 'insert' or 'modify' mode.
let flightModalMode = 'insert';

// ─── HELPERS ─────────────────────────────────────────────────────────────────
function parseTreeInput(raw) {
    if (raw === null || raw === undefined) return null;
    const text = String(raw).trim();
    if (!text) return null;
    const numericPattern = /^-?\d+(\.\d+)?$/;
    if (numericPattern.test(text)) {
        const asNumber = Number(text);
        return Number.isNaN(asNumber) ? text : asNumber;
    }
    return text;
}

function clearTraversalState() {
    highlighted.clear();
    pathNodes.clear();
    activeTrav = '';
    document.querySelectorAll('.trav-btn').forEach(b => b.classList.remove('active'));
}

/** Reset all flight modal fields to empty/default. */
function resetFlightModal() {
    document.getElementById('f-codigo').value       = '';
    document.getElementById('f-old-codigo').value   = '';
    document.getElementById('f-origen').value       = '';
    document.getElementById('f-destino').value      = '';
    document.getElementById('f-hora').value         = '';
    document.getElementById('f-pasajeros').value    = '';
    document.getElementById('f-precio-base').value  = '';
    document.getElementById('f-precio-final').value = '';
    document.getElementById('f-prioridad').value    = '2';
    document.getElementById('f-promocion').checked  = false;
    document.getElementById('f-alerta').checked     = false;
}

/** Read all flight fields from the modal and return a plain object. */
function readFlightModalData() {
    const codigo      = parseTreeInput(document.getElementById('f-codigo').value);
    const origen      = document.getElementById('f-origen').value.trim();
    const destino     = document.getElementById('f-destino').value.trim();
    const horaSalida  = document.getElementById('f-hora').value.trim();
    const pasajeros   = parseInt(document.getElementById('f-pasajeros').value)   || 0;
    const precioBase  = parseFloat(document.getElementById('f-precio-base').value) || 0;
    const precioFinalRaw = document.getElementById('f-precio-final').value.trim();
    const precioFinal = precioFinalRaw ? (parseFloat(precioFinalRaw) || precioBase) : precioBase;
    const prioridad   = parseInt(document.getElementById('f-prioridad').value)   || 2;
    const promocion   = document.getElementById('f-promocion').checked;
    const alerta      = document.getElementById('f-alerta').checked;

    return { codigo, origen, destino, horaSalida, pasajeros,
             precioBase, precioFinal, prioridad, promocion, alerta };
}

// ─── MODE ────────────────────────────────────────────────────────────────────
function setMode(m) {
    mode = m;
    document.getElementById('btn-bst').classList.toggle('active', m === 'BST');
    document.getElementById('btn-avl').classList.toggle('active', m === 'AVL');
    clearTree();
}

// ─── FLIGHT MODAL ────────────────────────────────────────────────────────────
/** Open modal in INSERT mode. */
function openInsertModal() {
    flightModalMode = 'insert';
    resetFlightModal();
    document.getElementById('flight-modal-title').textContent   = '✈ Nuevo Vuelo';
    document.getElementById('flight-modal-confirm').textContent = '＋ Insertar vuelo';
    document.getElementById('f-old-codigo-wrap').style.display  = 'none';
    document.getElementById('flight-modal-overlay').style.display = 'flex';
    document.getElementById('f-codigo').focus();
}

/** Open modal in MODIFY mode. Pre-fills code from sidebar input if available. */
function openModifyModal() {
    flightModalMode = 'modify';
    resetFlightModal();
    const currentVal = document.getElementById('val-input').value.trim();
    if (currentVal) document.getElementById('f-old-codigo').value = currentVal;
    document.getElementById('flight-modal-title').textContent   = '✏ Modificar Vuelo';
    document.getElementById('flight-modal-confirm').textContent = '✏ Confirmar modificación';
    document.getElementById('f-old-codigo-wrap').style.display  = 'block';
    document.getElementById('flight-modal-overlay').style.display = 'flex';
    document.getElementById('f-old-codigo').focus();
}

/** Close the flight modal. */
function closeFlightModal() {
    document.getElementById('flight-modal-overlay').style.display = 'none';
}

/** Confirm button — delegates to insert or modify based on current modal mode. */
async function confirmFlightModal() {
    if (flightModalMode === 'insert') {
        await _doInsert();
    } else {
        await _doModify();
    }
}

async function _doInsert() {
    const flight = readFlightModalData();
    if (!flight.codigo) { alert('El código del vuelo es obligatorio.'); return; }
    try {
        const data = await apiInsert(flight.codigo, mode, flight);
        root = data.arbol;
        closeFlightModal();
        addLog(`Insertado: ${flight.codigo} (${flight.origen} → ${flight.destino})`, 'ok');
        render();
    } catch (e) {
        addLog(`Error al insertar: ${e.message}`, 'err');
        alert(`Error al insertar: ${e.message}`);
    }
}

async function _doModify() {
    const oldCodigo = parseTreeInput(document.getElementById('f-old-codigo').value);
    const flight    = readFlightModalData();
    if (!oldCodigo)     { alert('El código actual del vuelo es obligatorio.'); return; }
    if (!flight.codigo) { alert('El nuevo código del vuelo es obligatorio.');  return; }
    try {
        const data = await apiModify(oldCodigo, flight.codigo, mode, flight);
        root = data.arbol;
        document.getElementById('val-input').value = '';
        closeFlightModal();
        addLog(`Modificado: ${oldCodigo} → ${flight.codigo}`, 'ok');
        render();
    } catch (e) {
        addLog(`Error al modificar: ${e.message}`, 'err');
        alert(`Error al modificar: ${e.message}`);
    }
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeFlightModal();
});

// ─── TREE OPERATIONS ─────────────────────────────────────────────────────────
async function deleteNode() {
    const v = parseTreeInput(document.getElementById('val-input').value);
    if (v === null) return;
    try {
        const data = await apiDelete(v, mode);
        root = data.arbol;
        document.getElementById('val-input').value = '';
        addLog(`Eliminado: ${v}`, 'err');
        render();
    } catch (e) {
        addLog(`Error al eliminar: ${e.message}`, 'err');
        alert(`Error al eliminar: ${e.message}`);
    }
}

async function cancelFlight() {
    const v = parseTreeInput(document.getElementById('val-input').value);
    if (v === null) { alert('Ingresa el código del vuelo a cancelar.'); return; }
    if (!confirm(`Se eliminará el vuelo ${v} y toda su descendencia. ¿Continuar?`)) return;
    try {
        const data = await apiCancel(v, mode);
        root = data.arbol;
        document.getElementById('val-input').value = '';
        addLog(`Cancelado (subárbol): ${v}`, 'err');
        render();
    } catch (e) {
        addLog(`Error al cancelar: ${e.message}`, 'err');
        alert(`Error al cancelar: ${e.message}`);
    }
}

async function undoAction() {
    try {
        const data = await apiUndo(mode);
        root = data.arbol;
        clearTraversalState();
        addLog(`Deshacer: ${data.undone_action || 'acción previa'}`, 'info');
        render();
    } catch (e) {
        addLog(`No se pudo deshacer: ${e.message}`, 'info');
    }
}

async function clearTree() {
    try {
        await apiClear();
        root = null;
        clearTraversalState();
        addLog('Árbol limpiado', 'info');
        render();
    } catch (e) {
        addLog(`Error al limpiar árbol: ${e.message}`, 'err');
        alert(`Error al limpiar árbol: ${e.message}`);
    }
}

function loadDemo() {
    root = null;
    [30, 20, 40, 10, 25, 35, 50].forEach(v => {
        root = mode === 'AVL' ? avlInsert(root, v) : bstInsert(root, v);
    });
    clearTraversalState();
    addLog('Demo cargado: [30,20,40,10,25,35,50]', 'ok');
    render();
}

// ─── TRAVERSAL ───────────────────────────────────────────────────────────────
async function runTraversal(type) {
    if (!root) return;
    try {
        const data = await apiTraversal(mode, type);
        highlighted = new Set(data.resultado);
        pathNodes.clear();
        activeTrav = type;
        document.querySelectorAll('.trav-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('t-' + type).classList.add('active');
        addLog(`${type}: [${data.resultado.join(', ')}]`, 'info');
        showResult(type, data.resultado, false);
        render();
    } catch (e) {
        addLog(`Error en recorrido ${type}: ${e.message}`, 'err');
        alert(`Error en recorrido ${type}: ${e.message}`);
    }
}

// ─── JSON ─────────────────────────────────────────────────────────────────────
function openJsonPicker() {
    document.getElementById('json-file-input').click();
}

async function handleJsonFileSelection(event) {
    const file = event.target.files && event.target.files[0];
    if (!file) return;
    try {
        const rawText    = await file.text();
        const parsedJson = JSON.parse(rawText);
        const data = await apiLoadJson(parsedJson);
        mode = 'AVL';
        root = data.main_avl || data.arbol || null;
        document.getElementById('btn-bst').classList.remove('active');
        document.getElementById('btn-avl').classList.add('active');
        clearTraversalState();
        render();
        addLog(`JSON cargado (${data.load_mode || 'auto'}) - Clave: ${data.detected_key || 'auto'}`, 'ok');
        openComparisonWindow(data.comparison, data.properties, data.load_mode, data.detected_key);
    } catch (e) {
        addLog(`Error de carga JSON: ${e.message}`, 'err');
        alert(`Error al cargar JSON: ${e.message}`);
    } finally {
        event.target.value = '';
    }
}

async function exportTreeJson() {
    try {
        const payload    = await apiExportJson(mode);
        const prettyJson = JSON.stringify(payload, null, 2);
        const blob       = new Blob([prettyJson], { type: 'application/json;charset=utf-8' });
        const url        = URL.createObjectURL(blob);
        const stamp      = new Date().toISOString().replace(/[:.]/g, '-');
        const link       = document.createElement('a');
        link.href        = url;
        link.download    = `skybalance-tree-export-${mode}-${stamp}.json`;
        document.body.appendChild(link);
        link.click();
        link.remove();
        URL.revokeObjectURL(url);
        addLog(`Exportado JSON (${mode})`, 'ok');
    } catch (e) {
        addLog(`Error al exportar JSON: ${e.message}`, 'err');
        alert(`Error al exportar JSON: ${e.message}`);
    }
}

// ─── VERSIONES ────────────────────────────────────────────────────────────────
async function saveVersion() {
    const name = document.getElementById('version-name-input').value.trim();
    if (!name) { alert('Escribe un nombre para la versión.'); return; }
    try {
        await apiVersionSave(name);
        document.getElementById('version-name-input').value = '';
        await loadVersionList();
        addLog(`Versión "${name}" guardada.`, 'ok');
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

async function loadVersionList() {
    try {
        const data   = await apiVersionList();
        const select = document.getElementById('version-select');
        select.innerHTML = '<option value="">-- Seleccionar versión --</option>';
        (data.versions || []).forEach(v => {
            const opt       = document.createElement('option');
            opt.value       = v.name;
            opt.textContent = `${v.name}  (${new Date(v.saved_at).toLocaleString()})`;
            select.appendChild(opt);
        });
    } catch (_) {}
}

async function restoreVersion() {
    const name = document.getElementById('version-select').value;
    if (!name) { alert('Selecciona una versión primero.'); return; }
    if (!confirm(`¿Restaurar "${name}"? El estado actual se guardará en el historial de deshacer.`)) return;
    try {
        const data = await apiVersionRestore(name, mode);
        root = data.arbol;
        render();
        addLog(`Versión "${name}" restaurada.`, 'ok');
    } catch (e) {
        alert(`Error: ${e.message}`);
    }
}

// ─── INIT ────────────────────────────────────────────────────────────────────
render();

document.addEventListener('keydown', (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'z') {
        event.preventDefault();
        undoAction();
    }
});