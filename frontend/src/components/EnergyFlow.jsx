/*
# src/components/EnergyFlow.jsx
*/

import { useEffect, useState } from "react";

export default function EnergyFlow({ data }) {
    const [flowData, setFlowData] = useState(null);
    const [hoverText, setHoverText] = useState(null);

    useEffect(() => {
        if (!data?.endpoint) return;

        fetch(`http://localhost:8000${data.endpoint}`)
            .then(res => res.json())
            .then(setFlowData)
            .catch(err => console.error(err));
    }, [data]);

    if (!flowData) {
        return (
            <div className="flex justify-center py-20 text-gray-500">
                Lade Energiefluss...
            </div>
        );
    }

    const nodes = flowData.nodes || [];
    const flows = flowData.flows || [];

    return (
        <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100 flex items-center justify-center p-6">

            {/* CARD */}
            <div className="w-full max-w-4xl bg-white rounded-2xl shadow-lg p-6">

                {/* HEADER */}
                <div className="mb-6">
                    <h2 className="text-xl font-semibold">
                        Energiefluss in deiner Community
                    </h2>
                    <p className="text-gray-500 text-sm">
                        So wird Energie aktuell verteilt
                    </p>
                </div>

                {/* SVG */}
                <svg
                    viewBox="0 0 600 400"
                    className="w-full h-[420px]"
                >

                    {/* FLOWS */}
                    {flows.map(f => (
                        <g key={f.id}>

                            {/* Linie */}
                            <path
                                d={f.path}
                                stroke={f.color}
                                strokeWidth={4}
                                fill="none"
                                strokeDasharray="6 6"
                                onMouseEnter={() =>
                                    setHoverText(
                                        `${f.from} → ${f.to} (${f.value} ${f.unit})`
                                    )
                                }
                                onMouseLeave={() => setHoverText(null)}
                            />

                            {/* animierter Punkt */}
                            <circle r="5" fill={f.color} style={{ filter: "drop-shadow(0 0 6px " + f.color + ")" }}>
                                <animateMotion
                                    dur="2.5s"
                                    repeatCount="indefinite"
                                    path={f.path}
                                />
                            </circle>

                        </g>
                    ))}

                    {/* NODES */}
                    {nodes.map(n => (
                        <g key={n.id} transform={`translate(${n.x}, ${n.y})`}>

                            {/* Glow */}
                            <circle r="30" fill="rgba(0,0,0,0.04)" />

                            {/* Node */}
                            <circle
                                r="24"
                                fill="white"
                                stroke={
                                    n.type === "solar" ? "#f97316" :
                                        n.type === "battery" ? "#10b981" :
                                            n.type === "grid" ? "#3b82f6" :
                                                "#d1d5db"
                                }
                                strokeWidth="2"
                            />

                            {/* Icon */}
                            <text
                                textAnchor="middle"
                                y="6"
                                fontSize="20"
                            >
                                {n.type === "solar" ? "☀️" :
                                    n.type === "battery" ? "🔋" :
                                        n.type === "grid" ? "⚡" :
                                            "🏠"}
                            </text>

                            {/* Label */}
                            <text
                                textAnchor="middle"
                                y="50"
                                className="text-xs fill-gray-600"
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

        </div>
    );
}
