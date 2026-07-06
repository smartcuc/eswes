/*
# src/features/energy/components/LiveEnergySankeyECharts.jsx
*/

import ReactECharts from "echarts-for-react";

function getNodeColor(node) {

    switch (node.id) {

        case "pv":
            return "#fbbf24";

        case "battery":
            return "#34d399";

        case "grid":
            return "#60a5fa";

        case "sum":
            return "#8b5cf6";
    }

    switch (node.type) {

        case "floor":
            return "#a855f7";

        case "room":
            return "#c084fc";

        case "consumer":
            return "#f472b6";

        case "untracked":
            return "#d1d5db";
    }

    return "#cbd5e1";
}

export default function LiveEnergySankeyECharts({ data }) {

    if (
        !data ||
        !Array.isArray(data.nodes) ||
        !Array.isArray(data.links)
    ) {
        return (
            <div className="text-gray-400">
                Keine Energiedaten
            </div>
        );
    }

    if (
        data.nodes.length === 0 ||
        data.links.length === 0
    ) {
        return (
            <div className="text-gray-400">
                Warten auf Live-Daten…
            </div>
        );
    }

    const nodes = data.nodes.map((node) => ({

        name: node.id,

        labelText: (() => {

            const value = node.value || 0;

            return value >= 1000
                ? `${node.label} (${(value / 1000).toFixed(1)} kW)`
                : `${node.label} (${value.toFixed(0)} W)`;

        })(),

        itemStyle: {
            color: getNodeColor(node),
        },

        rawLabel: node.label,
        nodeType: node.type,
    }));

    const links = data.links.map((link) => ({
        source: link.source,
        target: link.target,
        value: link.value,
    }));

    const option = {

        tooltip: {
            trigger: "item",
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

                        const node = data.nodes.find(
                            n => n.id === params.name
                        );

                        if (!node) {
                            return params.name;
                        }

                        const value = params.value || 0;

                        return value >= 1000
                            ? `${node.label}\n${(value / 1000).toFixed(1)} kW`
                            : `${node.label}\n${value.toFixed(0)} W`;
                    },
                },
            },
        ],
    };

    return (
        <div style={{ height: 550 }}>
            <ReactECharts
                option={option}
                style={{
                    height: "100%",
                    width: "100%",
                }}
            />
        </div>
    );
}
