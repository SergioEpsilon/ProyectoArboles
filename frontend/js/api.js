// api.js — All communication with the Flask backend.
// Single Responsibility: this file only handles HTTP requests/responses.

const API_BASE = 'http://127.0.0.1:5000';

async function readResponseOrThrow(response) {
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || 'La operación no pudo completarse.');
    return payload;
}

function postJSON(endpoint, body) {
    return fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
}

async function apiInsert(valor, modo)              { return readResponseOrThrow(await postJSON('/insert',       { valor, modo })); }
async function apiDelete(valor, modo)              { return readResponseOrThrow(await postJSON('/delete',       { valor, modo })); }
async function apiModify(old_valor, new_valor, modo, flight){
    return readResponseOrThrow(await postJSON('/modify', { old_valor, new_valor, modo, ...flight }));
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
    const res = await fetch(`${API_BASE}/version/list`);
    return readResponseOrThrow(res);
}