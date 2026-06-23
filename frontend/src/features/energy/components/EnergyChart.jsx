/*
# src/features/energy/components/EnergyChart.jsx
*/

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer
} from "recharts";

import { useMemo } from "react";
import { useEnergy } from "../context/EnergyContext";

export default function EnergyChart() {
    const { history } = useEnergy();

    // ✅ optional aggregieren (z.B. Gesamtleistung)
    const data = useMemo(() => {
        return history.map((h, i) => ({
            ...h,
            idx: i
        }));
    }, [history]);

    if (!data.length) {
        return <div className="text-gray-400">Warte auf Live-Daten…</div>;
    }

    return (
        <div style={{ height: 300 }}>
            <h3 style={{ marginBottom: 10 }}>📈 Live Leistungs‑Verlauf</h3>

            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                    <XAxis dataKey="idx" hide />
                    <YAxis />
                    <Tooltip />

                    <Line
                        type="monotone"
                        dataKey="value"
                        stroke="#3b82f6"
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={true}
                    />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
}
