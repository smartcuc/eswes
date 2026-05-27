//
// frontend/src/components/EventFeed.jsx
//

import { useCallback, useEffect, useState } from "react";
import { fetchEvents } from "../api/events";
import { useEventStream } from "../hooks/useEventStream";

export default function EventFeed() {
    const [status, setStatus] = useState("");
    const [events, setEvents] = useState([]);

    // History laden
    useEffect(() => {
        fetchEvents(status || null).then(setEvents).catch(console.error);
    }, [status]);

    // Live Updates
    const onMessage = useCallback((msg) => {
        setEvents((prev) => {
            const id = msg.event_id || msg.id;
            const normalized = {
                id,
                status: msg.status,
                tenant: msg.tenant_id ?? msg.tenant,
                event_type: msg.event_type || "METER_READING_BATCH",
                processed_at: msg.processed_at || null,
                error_message: msg.error_message || "",
                written: msg.written ?? null,
            };

            const idx = prev.findIndex((e) => e.id === id);
            let next = [...prev];
            if (idx >= 0) next[idx] = { ...next[idx], ...normalized };
            else next = [normalized, ...prev];

            if (status) next = next.filter((e) => e.status === status);
            return next.slice(0, 200);
        });
    }, [status]);

    const connected = useEventStream(onMessage);

    return (
        <div style={{ padding: 16, fontFamily: "system-ui" }}>
            <h2>Event Dashboard</h2>

            <div style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12 }}>
                <span>WS: {connected ? "🟢 verbunden" : "🟠 reconnect..."}</span>

                <label>
                    Status:&nbsp;
                    <select value={status} onChange={(e) => setStatus(e.target.value)}>
                        <option value="">(alle)</option>
                        <option value="RECEIVED">RECEIVED</option>
                        <option value="OK">OK</option>
                        <option value="ERROR">ERROR</option>
                        <option value="DUPLICATE">DUPLICATE</option>
                    </select>
                </label>

                <button onClick={() => fetchEvents(status || null).then(setEvents)}>
                    Refresh
                </button>
            </div>

            <table width="100%" cellPadding="8" style={{ borderCollapse: "collapse" }}>
                <thead>
                    <tr style={{ textAlign: "left", borderBottom: "1px solid #ddd" }}>
                        <th>Status</th><th>Event ID</th><th>Tenant</th><th>Processed</th><th>Error</th>
                    </tr>
                </thead>
                <tbody>
                    {events.map((e) => (
                        <tr key={e.id} style={{ borderBottom: "1px solid #f0f0f0" }}>
                            <td>{e.status}</td>
                            <td style={{ fontFamily: "monospace" }}>{e.id}</td>
                            <td style={{ fontFamily: "monospace" }}>{e.tenant || "-"}</td>
                            <td style={{ fontFamily: "monospace" }}>{e.processed_at || "-"}</td>
                            <td style={{ color: e.error_message ? "#b91c1c" : "#6b7280" }}>
                                {e.error_message || "-"}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
