/*
# src/components/EnergyFlow.jsx
*/

import useEnergyFlow from "../hooks/useEnergyFlow";

export default function EnergyFlow() {
    const data = useEnergyFlow();

    if (!data) {
        return <div className="text-gray-400">Lade Energiefluss...</div>;
    }

    const { flow } = data;

    // Node Positions (responsive-friendly viewbox)
    const nodes = {
        pv: { x: 100, y: 20 },
        house: { x: 100, y: 100 },
        battery: { x: 40, y: 180 },
        grid: { x: 160, y: 180 },
    };

    const flows = [
        {
            key: "pv_to_load",
            from: nodes.pv,
            to: nodes.house,
            value: flow.pv_to_load,
            color: "#facc15",
        },
        {
            key: "pv_to_battery",
            from: nodes.pv,
            to: nodes.battery,
            value: flow.pv_to_battery,
            color: "#facc15",
        },
        {
            key: "battery_to_load",
            from: nodes.battery,
            to: nodes.house,
            value: flow.battery_to_load,
            color: "#22c55e",
        },
        {
            key: "grid_to_load",
            from: nodes.grid,
            to: nodes.house,
            value: flow.grid_to_load,
            color: "#3b82f6",
        },
    ];

    return (
        <div className="w-full flex justify-center">
            <div className="relative w-full max-w-md">

                <svg viewBox="0 0 200 200" className="w-full h-auto">

                    {/* FLOW LINES */}
                    {flows.map((f) => (
                        <FlowLine key={f.key} {...f} />
                    ))}

                    {/* NODES */}
                    <Node {...nodes.pv} label="☀️" sub="PV" />
                    <Node {...nodes.house} label="🏠" sub="Haus" />
                    <Node {...nodes.battery} label="🔋" sub="Bat" />
                    <Node {...nodes.grid} label="⚡" sub="Netz" />

                </svg>

                {/* VALUE OVERLAY */}
                <div className="absolute inset-0 pointer-events-none">
                    {flows.map((f) => (
                        <FlowLabel key={f.key} {...f} />
                    ))}
                </div>
            </div>
        </div>
    );
}

/* ---------------- COMPONENTS ---------------- */

function FlowLine({ from, to, value, color }) {
    if (!value || value <= 0) return null;

    const strokeWidth = Math.max(2, value * 4);

    return (
        <line
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray="6 6"
            className="animate-flow"
        />
    );
}

function Node({ x, y, label, sub }) {
    return (
        <g transform={`translate(${x}, ${y})`}>
            <text
                textAnchor="middle"
                className="text-xl select-none"
                dy="-5"
            >
                {label}
            </text>
            <text
                textAnchor="middle"
                className="text-[10px] fill-gray-500"
                dy="10"
            >
                {sub}
            </text>
        </g>
    );
}

function FlowLabel({ from, to, value }) {
    if (!value || value <= 0) return null;

    const x = (from.x + to.x) / 2;
    const y = (from.y + to.y) / 2;

    return (
        <div
            style={{
                position: "absolute",
                left: `${x / 2}%`,
                top: `${y / 2}%`,
                transform: "translate(-50%, -50%)",
            }}
            className="text-xs text-gray-600 bg-white/70 px-1 rounded"
        >
            {value.toFixed(1)} kW
        </div>
    );
}
