import { useCallback, useState } from "react";
import { useEventStream } from "../hooks/useEventStream";

export default function WsTest() {
    const [last, setLast] = useState(null);

    const onMessage = useCallback((msg) => {
        console.log("🔥 WS EVENT", msg);
        setLast(msg);
    }, []);

    // ✅ dynamisch – funktioniert lokal UND in Produktion
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    const host = window.location.host;
    const wsUrl = `${protocol}://${host}/ws/events/`;

    const { connected } = useEventStream({
        url: wsUrl,
        onMessage
    });

    return (
        <div style={{ padding: 16, fontFamily: "system-ui" }}>
            <h3>WS Test</h3>
            <div>Status: {connected ? "🟢 verbunden" : "🟠 reconnect..."}</div>

            <pre
                style={{
                    marginTop: 12,
                    background: "#111",
                    color: "#0f0",
                    padding: 12,
                    borderRadius: 8
                }}
            >
                {last ? JSON.stringify(last, null, 2) : "Noch kein Event empfangen"}
            </pre>
        </div>
    );
}