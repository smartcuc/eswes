/*
# src/features/energy/hooks/useEnergySocket.js
*/

import { useEffect, useRef, useState, useCallback } from "react";

/*
# ✅ WebSocket Hook (Production Ready)
*/
export default function useEnergySocket(onMessage) {
    const socketRef = useRef(null);

    useEffect(() => {

        let reconnectTimer;

        function getWsUrl() {
            const protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
            return protocol + window.location.host + "/ws/energy/";
        }

        function connect() {
            const url = getWsUrl();

            const socket = new WebSocket(url);
            socketRef.current = socket;

            socket.onopen = () => {
                console.log("✅ WebSocket connected");
            };

            let lastUpdate = 0; // ✅ throttle state

            socket.onmessage = (event) => {
                const now = Date.now();

                // ✅ THROTTLE (max 2 Updates/sec)
                if (now - lastUpdate < 500) return;

                lastUpdate = now;

                try {
                    const data = JSON.parse(event.data);

                    // ✅ nur relevante Events
                    if (data?.type === "metric_update") {

                        // 🔥 CRITICAL FIX
                        if (typeof onMessage === "function") {
                            onMessage(data);
                        }
                    }

                } catch (e) {
                    console.error("❌ WS parse error", e);
                }
            };

            socket.onerror = (err) => {
                console.error("❌ WebSocket error", err);
                socket.close();
            };

            socket.onclose = () => {
                console.warn("⚠️ WebSocket closed → reconnecting...");
                reconnectTimer = setTimeout(connect, 2000);
            };
        }

        connect();

        // ✅ Cleanup
        return () => {
            if (reconnectTimer) clearTimeout(reconnectTimer);

            if (socketRef.current) {
                socketRef.current.close();
            }
        };

    }, [onMessage]);
}

