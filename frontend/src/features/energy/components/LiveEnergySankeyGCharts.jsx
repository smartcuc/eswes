/*
# src/features/energy/components/LiveEnergySankeyECharts.jsx
*/

import ReactECharts from "echarts-for-react";
import { useEffect, useRef } from "react";

function getNodeColor(node) {
    switch (node.id) {
        case "pv": return "#fbbf24";
        case "battery": return "#34d399";
        case "grid": return "#60a5fa";
        case "sum": return "#8b5cf6";
        default:
            switch (node.type) {
                case "floor": return "#a855f7";
                case "room": return "#c084fc";
                case "consumer": return "#f472b6";
                case "untracked": return "#d1d5db";
                default: return "#cbd5e1";
            }
    }
}

export default function LiveEnergySankeyECharts({ data }) {
    const chartRef = useRef(null);

    useEffect(() => {
        return () => {
            if (chartRef.current) {
                const echartsInstance = chartRef.current.getEchartsInstance();
                if (echartsInstance && !echartsInstance.isDisposed()) {
                    echartsInstance.dispose(); // Zerstört die Instanz im DOM restlos
                }
            }
        };
    }, []);

    if (!data || !Array.isArray(data.nodes) || !Array.isArray(data.links)) {
        return <div className="text-gray-400">Keine Energiedaten</div>;
    }

    if (data.nodes.length === 0 || data.links.length === 0) {
        return <div className="text-gray-400">Warten auf Live-Daten…</div>;
    }

    // Nodes vorbereiten
    const nodes = data.nodes.map((node) => ({
        name: node.id,
        itemStyle: {
            color: getNodeColor(node),
        },
        rawLabel: node.label,
        nodeType: node.type,
    }));

    // Links filtern (Verhindert Geister-Linien mit dem Wert 0)
    const links = data.links
        .filter(link => link.value > 0)
        .map((link) => ({
            source: link.source,
            target: link.target,
            value: link.value,
        }));

    const option = {
        tooltip: {
            trigger: "item",
            formatter: (params) => {
                if (params.dataType === 'edge') {
                    return `${params.data.source} → ${params.data.target}: <b>${params.data.value.toFixed(0)} W</b>`;
                }
                return `${params.name}: <b>${params.value.toFixed(0)} W</b>`;
            }
        },
        series: [
            {
                type: "sankey",
                left: 120,
                right: 60,
                top: 20,
                bottom: 20,
                data: nodes,
                links,
                nodeWidth: 18,
                nodeGap: 24,
                draggable: false,

                // 🔥 CRITICAL FIX 1: Verhindert, dass Nodes bei Werteänderungen die Plätze tauschen
                layoutIterations: 0,

                emphasis: {
                    focus: "adjacency",
                },
                lineStyle: {
                    color: "gradient",
                    opacity: 0.35,
                    curveness: 0.5,
                },
                label: {
                    color: "#374151",
                    fontSize: 12,
                    formatter: (params) => {
                        // Sicherer Fallback-Check
                        const node = data.nodes.find(n => n.id === params.name);
                        const label = node ? node.label : params.name;
                        const value = params.value || 0;

                        return value >= 1000
                            ? `${label}\n${(value / 1000).toFixed(1)} kW`
                            : `${label}\n${value.toFixed(0)} W`;
                    },
                },
            },
        ],
    };

    return (
        <div style={{ height: 550 }}>
            <ReactECharts
                ref={chartRef}
                option={option}
                style={{ height: "100%", width: "100%" }}
                // 🔥 CRITICAL FIX 2: Lässt ECharts die Werte flüssig animieren statt neu zu bauen
                notMerge={false}
                lazyUpdate={true}
            />
        </div>
    );
}
