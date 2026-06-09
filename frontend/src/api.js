/*
# src/api.js
*/

export function apiFetch(url, options = {}) {
    const token = localStorage.getItem("access");

    return fetch(url, {
        method: options.method || "GET",
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: options.body,
    });
}
