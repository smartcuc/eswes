/*
# src/components/EnergyFlow.jsx
*/

export default function EnergyFlow({ data }) {

    if (!data || !data.flow) {
        return <div className="text-gray-400">Keine Energiedaten</div>;
    }

    const { flow } = data;

    const nodes = {
        pv: { x: 100, y: 20, icon: "☀️" },
        house: { x: 100, y: 110, icon: "🏠" },
        battery: { x: 60, y: 180, icon: "🔋" },
        grid: { x: 140, y: 180, icon: "⚡" },
    };

    const flows = [
        {
            id: "pv_to_load",
            from: nodes.pv,
            to: nodes.house,
            value: flow.pv_to_load,
            color: "#fbbf24",
        },
        {
            id: "pv_to_battery",
            from: nodes.pv,
            to: nodes.battery,
            value: flow.pv_to_battery,
            color: "#fde68a",
        },
        {
            id: "battery_to_load",
            from: nodes.battery,
            to: nodes.house,
            value: flow.battery_to_load,
            color: "#4ade80",
        },
        {
            id: "grid_import",
            from: nodes.grid,
            to: nodes.house,
            value: flow.grid_to_load,
            color: "#60a5fa",
        },
        {
            id: "grid_export",
            from: nodes.house,
            to: nodes.grid,
            value: flow.grid_export || 0,
            color: "#93c5fd",
        },
    ];

    const max = Math.max(...flows.map(f => f.value || 0), 1);

    return (
        <div className="w-full flex justify-center">
            <div className="relative w-full max-w-md">

                <svg viewBox="0 0 200 200" className="w-full">

                    {/* ✅ FLOW LINES */}
                    {flows.map(f => (
                        <FlowLine
                            key={f.id}
                            {...f}
                            max={max}
                        />
                    ))}

                    {/* ✅ NODES (ohne Status-Label!) */}
                    <Node {...nodes.pv} />
                    <Node {...nodes.battery} />
                    <Node {...nodes.grid} />
                    <Node {...nodes.house} />

                </svg>

                {/* ✅ FLOW LABELS (Energie-Werte bleiben!) */}
                <div className="absolute inset-0 pointer-events-none">
                    {flows.map(f => (
                        <FlowLabel key={f.id} {...f} />
                    ))}
                </div>

            </div>
        </div>
    );
}


/* ---------------- FLOW LINE ---------------- */

function FlowLine({ from, to, value, color, max }) {
    if (!value || value <= 0) return null;

    const width = Math.max(1.5, value / 2000);
    const opacity = 0.3 + (value / max) * 0.7;

    return (
        <line
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke={color}
            strokeWidth={width}
            strokeOpacity={opacity}
            strokeLinecap="round"
        />
    );
}


/* ---------------- NODE ---------------- */

function Node({ x, y, icon }) {
    return (
        <g transform={`translate(${x}, ${y})`}>

            <circle
                r="14"
                fill="white"
                opacity="0.08"
            />

            <text textAnchor="middle" dy="6">
                {icon}
            </text>

        </g>
    );
}


/* ---------------- FLOW LABEL ---------------- */

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
            className="text-[11px] text-gray-600 bg-white/80 px-2 py-0.5 rounded-md"
        >
            {(value / 1000).toFixed(1)} kW
        </div>
    );
}
