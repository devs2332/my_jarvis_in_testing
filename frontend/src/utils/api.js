
const API = '' // Use translation proxy or absolute URL if needed

function getHeaders(customHeaders = {}) {
    const token = localStorage.getItem('jarvis_token');
    const headers = { ...customHeaders };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

export async function fetchJSON(path) {
    const res = await fetch(`${API}${path}`, {
        headers: getHeaders()
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
}

export async function postJSON(path, body) {
    const res = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: getHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify(body),
    });
    if (!res.ok) {
        let msg = `API Error: ${res.status}`;
        try {
            const errBody = await res.json();
            if (errBody.detail) msg = errBody.detail;
        } catch (e) { }
        throw new Error(msg);
    }
    return res.json();
}

export async function deleteJSON(path) {
    const res = await fetch(`${API}${path}`, {
        method: 'DELETE',
        headers: getHeaders()
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
}
