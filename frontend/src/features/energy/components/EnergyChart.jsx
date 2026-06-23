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
    const energy = useEnergy();
    const history = energy?.history;

    // ✅ Immer Hooks oben
    const data = useMemo(() => {
        if (!history || !Array.isArray(history)) return [];

        return history.map((h, i) => ({
            idx: i,
            value: h?.value ?? 0
        }));
    }, [history]);

    // ✅ danach erst Guards

    if (!history || !Array.isArray(history)) {
        return <div>Loading chart…</div>;
    }

    if (history.length === 0) {
        return <div>No data yet</div>;
    }

    if (!data.length) {
        return <div className="text-gray-400">Warte auf Live-Daten…</div>;
    }

    return (
        <div style={{ height: 300 }}>
            <h3 style={{ marginBottom: 10 }}>
                📈 Live Leistungs‑Verlauf
            </h3>

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

