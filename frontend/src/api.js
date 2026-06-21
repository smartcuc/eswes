/*
# src/api.js
*/

export function apiFetchi(url, options = {}) {
    return fetch(url, {
        method: options.method || "GET",
        headers: {
            "Content-Type": "application/json",
            ...(options.headers || {}),
        },
        body: options.body,

        credentials: "include", // 💥 DAS IST DER KEY FIX
    });
}
