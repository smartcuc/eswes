/*
# src/components/UserEnergyPanel.jsx
*/

import { useEffect, useState } from "react";

export default function UserEnergyPanel() {
    const [power, setPower] = useState(0);

    useEffect(() => {
        const socket = new WebSocket("ws://localhost:8000/ws/energy");

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            setPower(data.power);
        };

        return () => socket.close();
    }, []);

    return (
        <div style={{ padding: "2rem" }}>
            <h3>Dein aktueller Verbrauch</h3>
            <div style={{ fontSize: "2rem" }}>{power} W</div>
        </div>
    );
}
