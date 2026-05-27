//#####################################
// frontend/src/hooks/useEventStream.js
//#####################################

import { useEffect, useRef, useState } from "react";

export function useEventStream({ url, onMessage, enabled = true }) {
    const [connected, setConnected] = useState(false);
    const wsRef = useRef(null);

    useEffect(() => {
        if (!enabled) return;

        let retry = 0;
        let closedByUs = false;

        const connect = () => {
            const ws = new WebSocket(url);
            wsRef.current = ws;

            ws.onopen = () => {
                setConnected(true);
                retry = 0;
            };

            ws.onmessage = (ev) => {
                try {
                    const data = JSON.parse(ev.data);
                    onMessage?.(data);
                } catch {
                    // ignore parse errors
                }
            };

            ws.onclose = () => {
                setConnected(false);
                if (closedByUs) return;
                const delay = Math.min(10000, 500 * 2 ** retry);
                retry += 1;
                setTimeout(connect, delay);
            };

            ws.onerror = () => ws.close();
        };

        connect();

        return () => {
            closedByUs = true;
            wsRef.current?.close();
        };
    }, [url, onMessage, enabled]);

    return { connected };
}
