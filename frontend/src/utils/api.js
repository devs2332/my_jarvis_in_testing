
const API = '' // Use translation proxy or absolute URL if needed

export async function fetchJSON(path) {
    const res = await fetch(`${API}${path}`)
    if (!res.ok) throw new Error(`API Error: ${res.status}`)
    return res.json()
}

export async function postJSON(path, body) {
    const res = await fetch(`${API}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
    })
    if (!res.ok) throw new Error(`API Error: ${res.status}`)
    return res.json()
}

export async function deleteJSON(path) {
    const res = await fetch(`${API}${path}`, {
        method: 'DELETE',
    })
    if (!res.ok) throw new Error(`API Error: ${res.status}`)
    return res.json()
}
