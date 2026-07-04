/*
# src/features/energy/components/LiveEnergySankey.jsx
*/

import { ResponsiveSankey } from "@nivo/sankey";

export default function LiveEnergySankey({ data }) {

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

    return (
        <div style={{ height: 550 }}>

            <ResponsiveSankey
                data={data}
                nodeThickness={18}
                nodeSpacing={24}
                animate={true}
                motionConfig="gentle"

                label={(node) => {
                    const value = node.value || 0;

                    return value >= 1000
                        ? `${node.label} (${(value / 1000).toFixed(1)} kW)`
                        : `${node.label} (${value.toFixed(0)} W)`;
                }}

                // label={(node) => node.label}
                labelPosition="outside"
                labelOrientation="horizontal"
                nodeOpacity={1}
                linkOpacity={0.5}
                margin={{
                    top: 20,
                    right: 40,
                    bottom: 20,
                    left: 80,
                }}
                colors={(node) => {

                    switch (node.id) {

                        case "pv":
                            return "#f59e0b";

                        case "battery":
                            return "#10b981";

                        case "grid":
                            return "#6366f1";

                        case "sum":
                            return "#64748b";

                        default:
                            return "#ef4444";
                    }
                }}
            />

        </div>
    );
}
