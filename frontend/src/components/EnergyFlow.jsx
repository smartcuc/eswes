/*
# src/components/EnergyFlow.jsx
*/

import { useEffect, useState } from "react";

export default function EnergyFlow({ mode = "demo", endpoint = null }) {

    const [flowData, setFlowData] = useState(null);
    const [hoverText, setHoverText] = useState(null);

    useEffect(() => {

        // ✅ DEMO MODE (Landing)
        if (mode === "demo") {
            setFlowData(getDemoFlow());
            return;
        }

        // ✅ LIVE MODE (Dashboard)
        if (mode === "live" && endpoint) {
            fetch(endpoint)
                .then(res => res.json())
                .then(setFlowData)
                .catch(() => setFlowData(getDemoFlow()));
        }

    }, [mode, endpoint]);

    if (!flowData) {
        return <div className="text-gray-400 text-center py-10">Lade Energiefluss...</div>;
    }

    const { nodes, flows } = flowData;

    return (
        <div className="bg-white rounded-2xl shadow-xl p-8 max-w-3xl mx-auto">

            <h2 className="text-xl font-semibold text-center mb-6">
                Energie fließt live
            </h2>

            <svg viewBox="0 0 500 300" className="w-full">

                {/* FLOWS */}
                {flows.map(f => (
                    <g key={f.id}>

                        {/* Hover area */}
                        <path
                            d={f.path}
                            stroke="transparent"
                            strokeWidth="20"
                            fill="none"
                            onMouseEnter={() => setHoverText(f.label)}
                            onMouseLeave={() => setHoverText(null)}
                        />

                        {/* visible line */}
                        <path
                            d={f.path}
                            stroke={f.color}
                            strokeWidth="3"
                            fill="none"
                            strokeOpacity="0.4"
                        />

                        {/* moving dots */}
                        {[0, 0.8].map((delay, i) => (
                            <circle key={i} r="5" fill={f.color}>
                                <animateMotion
                                    dur={`${f.speed}s`}
                                    begin={`${delay}s`}
                                    repeatCount="indefinite"
                                    path={f.path}
                                />
                            </circle>
                        ))}

                    </g>
                ))}

                {/* NODES */}
                {nodes.map(n => (
                    <g key={n.id} transform={`translate(${n.x}, ${n.y})`}>

                        <circle
                            r="28"
                            fill={n.type === "solar" ? "#fb923c20" : "#6366f120"}
                        />

                        <rect
                            x="-20"
                            y="-20"
                            width="40"
                            height="40"
                            rx="10"
                            fill={n.type === "solar" ? "#fb923c" : "#6366f1"}
                        />

                        <text
                            textAnchor="middle"
                            y="6"
                            fontSize="18"
                            fill="white"
                        >
                            {n.icon}
                        </text>

                        <text
                            textAnchor="middle"
                            y="40"
                            fontSize="12"
                            fill="#666"
                        >
                            {n.name}
                        </text>

                    </g>
                ))}

            </svg>

            {/* TOOLTIP */}
            {hoverText && (
                <div className="mt-4 text-center text-sm text-gray-700">
                    {hoverText}
                </div>
            )}

        </div>
    );
}


/* ✅ DEMO DATA */
function getDemoFlow() {
    return {
        nodes: [
            { id: 1, name: "Solar", x: 100, y: 220, type: "solar", icon: "☀️" },
            { id: 2, name: "Haus A", x: 400, y: 200, type: "home", icon: "🏠" },
            { id: 3, name: "Haus B", x: 250, y: 80, type: "home", icon: "🏠" },
        ],
        flows: [
            {
                id: 1,
                label: "Solar → Haus A (5 kWh)",
                color: "#f97316",
                path: "M100,220 Q250,140 400,200",
                speed: 2
            },
            {
                id: 2,
                label: "Solar → Haus B (3 kWh)",
                color: "#ec4899",
                path: "M100,220 Q180,150 250,80",
                speed: 3
            },
            {
                id: 3,
                label: "Haus B → Haus A (2 kWh)",
                color: "#6366f1",
                path: "M250,80 Q340,140 400,200",
                speed: 2.5
            }
        ]
    };
}