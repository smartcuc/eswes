import { useCallback, useState } from "react";
import { useEventStream } from "../hooks/useEventStream";

export default function WsTest() {
    const [last, setLast] = useState(null);

    const onMessage = useCallback((msg) => {
        console.log("🔥 WS EVENT", msg);
        setLast(msg);
    }, []);

    // Direkt auf Daphne (am sichersten fürs Debugging)
    const { connected } = useEventStream({
        url: "ws://127.0.0.1:8000/ws/events/",
        onMessage
    });

    return (
        <div style={{ padding: 16, fontFamily: "system-ui" }}>
            <h3>WS Test</h3>
            <div>Status: {connected ? "🟢 verbunden" : "🟠 reconnect..."}</div>
            <pre style={{ marginTop: 12, background: "#111", color: "#0f0", padding: 12, borderRadius: 8 }}>
                {last ? JSON.stringify(last, null, 2) : "Noch kein Event empfangen"}
            </pre>
        </div>
    );
}