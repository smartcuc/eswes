import { useState } from "react";

export default function EnergyFlow() {

    const [hoverText, setHoverText] = useState(null);

    const nodes = [
        { id: 1, name: "Müller", x: 100, y: 220, type: "solar" },
        { id: 2, name: "Schmidt", x: 400, y: 200, type: "home" },
        { id: 3, name: "Wagner", x: 250, y: 80, type: "home" },
    ];

    const flows = [
        {
            id: 1,
            label: "Müller → Schmidt (5 kWh)",
            color: "#f97316",
            path: "M100,220 Q250,140 400,200",
            speed: 2
        },
        {
            id: 2,
            label: "Müller → Wagner (3 kWh)",
            color: "#ec4899",
            path: "M100,220 Q180,150 250,80",
            speed: 3
        },
        {
            id: 3,
            label: "Wagner → Schmidt (4 kWh)",
            color: "#6366f1",
            path: "M250,80 Q340,140 400,200",
            speed: 2.5
        }
    ];

    return (
        <div className="bg-white rounded-2xl shadow-xl p-10 max-w-3xl mx-auto mt-16">

            <h2 className="text-2xl font-semibold text-center mb-8">
                Energie bewegt deine Nachbarschaft
            </h2>

            <div className="relative">

                <svg viewBox="0 0 500 300" className="w-full">

                    {/* FLOWS */}
                    {flows.map(f => (
                        <g key={f.id}>

                            {/* dicke unsichtbare Hoverlinie */}
                            <path
                                d={f.path}
                                stroke="transparent"
                                strokeWidth="20"
                                fill="none"
                                onMouseEnter={() => setHoverText(f.label)}
                                onMouseLeave={() => setHoverText(null)}
                            />

                            {/* sichtbare Linie */}
                            <path
                                d={f.path}
                                stroke={f.color}
                                strokeWidth="2"
                                fill="none"
                                strokeOpacity="0.3"
                            />

                            {/* Punkte */}
                            {[0, 0.7].map((delay, i) => (
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

                    {/* NODES INS SVG → JETZT PERFEKT POSITIONIERT */}
                    {nodes.map(n => (

                        <g key={n.id}
                            transform={`translate(${n.x}, ${n.y})`}>

                            {/* Node Background */}
                            <rect
                                x="-25"
                                y="-25"
                                width="50"
                                height="50"
                                rx="12"
                                fill={n.type === "solar" ? "#fb923c" : "#6366f1"}
                            />

                            {/* Icon */}
                            <text
                                textAnchor="middle"
                                y="5"
                                fontSize="20"
                                fill="white"
                            >
                                {n.type === "solar" ? "☀️" : "🏠"}
                            </text>

                            {/* Label */}
                            <text
                                textAnchor="middle"
                                y="45"
                                fontSize="12"
                                fill="#555"
                            >
                                {n.name}
                            </text>

                        </g>
                    ))}

                </svg>

                {/* TOOLTIP */}
                {hoverText && (
                    <div className="
                        absolute top-0 left-1/2 -translate-x-1/2
                        bg-white shadow-lg px-4 py-2 rounded-lg text-sm
                        border border-gray-200
                    ">
                        {hoverText}
                    </div>
                )}

            </div>

        </div>
    );
}