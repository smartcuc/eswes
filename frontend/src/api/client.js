/*
# src/api/client.js
*/

import { getCSRFToken } from "../lib/csrf";

export async function apiFetch(url, options = {}) {
    // Standard-Header definieren
    const defaultHeaders = {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
    };

    const res = await fetch(url, {
        ...options,
        credentials: "include",
        // Kombiniert Standard-Header mit benutzerdefinierten Headern aus options
        headers: {
            ...defaultHeaders,
            ...(options.headers || {}),
        },
    });

    // ✅ 401 / 403 → Session weg → Logout
    if (res.status === 401 || res.status === 403) {
        console.warn("Auth lost → redirecting to login");

        localStorage.clear();
        sessionStorage.clear();

        throw { type: "auth" };
        // Abbrechen, da der Redirect läuft
        //        return new Promise(() => { });
    }

    // ✅ 400 → Validierungsfehler
    if (res.status === 400) {
        let data;
        try {
            data = await res.json();
        } catch {
            data = { error: "Bad Request" };
        }

        throw {
            type: "validation",
            data,
        };
    }

    // ✅ Andere Server-Fehler (500, 404, etc.)
    if (!res.ok) {
        const text = await res.text();
        throw {
            type: "server",
            message: text || "Server error",
        };
    }

    // ✅ 204 No Content abfangen, um JSON-Parse-Fehler zu vermeiden
    if (res.status === 204) {
        return null;
    }

    // ✅ Erfolg
    return res.json();
}
