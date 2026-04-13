// api.js — All communication with the Flask backend.
// Single Responsibility: this file only handles HTTP requests/responses.

const API_BASE = 'http://127.0.0.1:5000';

function backendConnectionError() {
    return new Error('No se pudo conectar con el backend. Verifica que Flask esté ejecutándose en http://127.0.0.1:5000.');
}

async function readResponseOrThrow(response) {
    try {
        const payload = await response.json();
        if (!response.ok) throw new Error(payload.error || 'La operación no pudo completarse.');
        return payload;
    } catch (error) {
        if (error instanceof SyntaxError) {
            throw new Error('La respuesta del backend no es válida.');
        }
        throw error;
    }
}

async function fetchJSON(url, options) {
    try {
        return await fetch(url, options);
    } catch (_) {
        throw backendConnectionError();
    }
}

function postJSON(endpoint, body) {
    return fetchJSON(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
}

async function apiInsert(valor, modo, flight)      { return readResponseOrThrow(await postJSON('/insert',       { valor, modo, ...(flight || {}) })); }
async function apiDelete(valor, modo)              { return readResponseOrThrow(await postJSON('/delete',       { valor, modo })); }
async function apiModify(old_valor, new_valor, modo, flight){
    return readResponseOrThrow(await postJSON('/modify', { old_valor, new_valor, modo, ...(flight || {}) }));
}
async function apiCancel(valor, modo)              { return readResponseOrThrow(await postJSON('/cancel',       { valor, modo })); }
async function apiUndo(modo)                       { return readResponseOrThrow(await postJSON('/undo',         { modo })); }
async function apiClear()                          { return readResponseOrThrow(await postJSON('/clear',        {})); }
async function apiTraversal(modo, tipo)            { return readResponseOrThrow(await postJSON('/traversal',    { modo, tipo })); }
async function apiExportJson(modo)                 { return readResponseOrThrow(await postJSON('/export-json',  { modo })); }
async function apiLoadJson(json_data)              { return readResponseOrThrow(await postJSON('/load-json',    { json_data })); }
async function apiVersionSave(name)                { return readResponseOrThrow(await postJSON('/version/save', { name })); }
async function apiVersionRestore(name, modo)       { return readResponseOrThrow(await postJSON('/version/restore', { name, modo })); }
async function apiVersionList() {
    const res = await fetchJSON(`${API_BASE}/version/list`);
    return readResponseOrThrow(res);
}

async function apiQueueEnqueue(valor, modo, flow_id) {
    return readResponseOrThrow(await postJSON('/queue/enqueue', { valor, modo, flow_id }));
}

async function apiQueueList(modo) {
    const res = await fetchJSON(`${API_BASE}/queue/list?modo=${encodeURIComponent(modo)}`);
    return readResponseOrThrow(res);
}

async function apiQueueProcess(modo, flow_slots) {
    return readResponseOrThrow(await postJSON('/queue/process', { modo, flow_slots }));
}

async function apiMetrics(modo) {
    const res = await fetchJSON(`${API_BASE}/metrics?modo=${encodeURIComponent(modo)}`);
    return readResponseOrThrow(res);
}

async function apiMetricsReset() {
    return readResponseOrThrow(await postJSON('/metrics/reset', {}));
}

// ── Stress Mode (Point 5) ─────────────────────────────────────────────────────
async function apiStressStatus() {
    const res = await fetchJSON(`${API_BASE}/stress/status`);
    return readResponseOrThrow(res);
}
async function apiStressEnable()    { return readResponseOrThrow(await postJSON('/stress/enable',    {})); }
async function apiStressDisable()   { return readResponseOrThrow(await postJSON('/stress/disable',   {})); }
async function apiStressRebalance() { return readResponseOrThrow(await postJSON('/stress/rebalance', {})); }
// ── Depth Penalty (Point 6) ───────────────────────────────────────────────────
async function apiDepthLimitGet() {
    const res = await fetchJSON(`${API_BASE}/depth-limit/get`);
    return readResponseOrThrow(res);
}
async function apiDepthLimitSet(depth) {
    return readResponseOrThrow(await postJSON('/depth-limit/set', { depth }));
}

async function apiStressAudit() {
    const res = await fetchJSON(`${API_BASE}/stress/audit`);
    return readResponseOrThrow(res);
}

async function apiEconomicDelete() {
    return readResponseOrThrow(await postJSON('/economic-delete', {}));
}