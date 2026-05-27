//
//
//

import { useState, useCallback, useMemo } from "react";
import { useEventStream } from "../hooks/useEventStream";

export default function EventDashboard() {
    const [events, setEvents] = useState([]);
    const [selected, setSelected] = useState(null);

    // ✅ stabile Callback-Funktion (wichtig, damit der WS nicht dauernd neu startet)
    const onWsMessage = useCallback((msg) => {
        const id = msg.event_id;
        if (!id) return;

        setEvents((prev) => {
            const idx = prev.findIndex((e) => e.id === id);

            if (idx >= 0) {
                const updated = [...prev];
                updated[idx] = { ...updated[idx], ...msg, id };
                return updated;
            }

            return [{ id, ...msg }, ...prev];
        });
    }, []);

    // ✅ WebSocket (direkt zu Daphne)
    const { connected } = useEventStream({
        url: "ws://127.0.0.1:8000/ws/events/",
        onMessage: onWsMessage,
        enabled: true,
    });

    // ✅ KPIs (useMemo damit es nicht bei jedem Render teuer wird)
    const kpis = useMemo(() => {
        const total = events.length;
        const ok = events.filter((e) => e.status === "OK").length;
        const error = events.filter((e) => e.status === "ERROR").length;
        return { total, ok, error };
    }, [events]);

    // ✅ Replay
    const replayEvent = useCallback((id) => {
        fetch(`http://127.0.0.1:8000/api/v1/events/${id}/replay/`, {
            method: "POST",
        }).catch(console.error);
    }, []);

    return (
        <div style={{ padding: 20 }}>
            <h2>Realtime Dashboard</h2>

            <div>WS: {connected ? "🟢 connected" : "🟠 reconnecting"}</div>

            {/* ✅ KPIs */}
            <div style={{ display: "flex", gap: 20, marginTop: 20 }}>
                <div>Total: {kpis.total}</div>
                <div style={{ color: "green" }}>OK: {kpis.ok}</div>
                <div style={{ color: "red" }}>ERROR: {kpis.error}</div>
            </div>

            {/* ✅ Tabelle */}
            <table style={{ width: "100%", marginTop: 20 }}>
                <thead>
                    <tr>
                        <th>Status</th>
                        <th>ID</th>
                        <th>Tenant</th>
                        <th>Processed</th>
                        <th>Replay</th>
                    </tr>
                </thead>

                <tbody>
                    {events.map((e) => (
                        <tr
                            key={e.id}
                            style={{
                                background: e.status === "ERROR" ? "#ffe5e5" : "white",
                                cursor: "pointer",
                            }}
                            onClick={() => setSelected(e)}
                        >
                            <td>{e.status}</td>
                            <td style={{ fontFamily: "monospace" }}>{e.id}</td>
                            <td style={{ fontFamily: "monospace" }}>{e.tenant_id || "-"}</td>
                            <td style={{ fontFamily: "monospace" }}>{e.processed_at || "-"}</td>

                            <td>
                                {e.status === "ERROR" && (
                                    <button
                                        onClick={(ev) => {
                                            ev.stopPropagation();
                                            replayEvent(e.id);
                                        }}
                                    >
                                        Replay
                                    </button>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>

            {/* ✅ Details */}
            {selected && (
                <div style={{ marginTop: 20 }}>
                    <h3>Event Details</h3>
                    <pre>{JSON.stringify(selected, null, 2)}</pre>
                    <button onClick={() => setSelected(null)}>Schließen</button>
                </div>
            )}
        </div>
    );
}