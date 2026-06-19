/*
# src/lib/track.jsx
*/

import { apiFetch } from "../api/client";

let queue = [];
let timer = null;

function sendBatch() {
    if (queue.length === 0) return;

    const batch = [...queue];
    queue = [];

    apiFetch("/api/track/", {
        method: "POST",
        body: JSON.stringify({ events: batch }),
    }).catch(() => {
        // optional: retry könnte hier rein
    });
}

export function trackEvent(event, metadata = {}) {
    queue.push({
        event,
        metadata,
        ts: new Date().toISOString(),
    });

    // ✅ Timer starten (Batch nach Delay senden)
    if (!timer) {
        timer = setTimeout(() => {
            sendBatch();
            timer = null;
        }, 1000); // 1 Sekunde debounce
    }

    // ✅ Backup: wenn zu viele Events → sofort senden
    if (queue.length >= 10) {
        clearTimeout(timer);
        sendBatch();
        timer = null;
    }
}

/*
Empfohlene Option, oben aber besser was nun?

import { apiFetch } from "../api/client";

export function trackEvent(event, metadata = {}) {
    apiFetch("/api/track/", {
        method: "POST",
        body: JSON.stringify({
            event,
            metadata,
        }),
    }).catch(() => {
        // absichtlich ignorieren
    });
}
*/