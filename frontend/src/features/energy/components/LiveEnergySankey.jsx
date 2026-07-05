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
                animate={true}
                motionConfig="gentle"

                label={(node) => {
                    const value = node.value || 0;

                    return value >= 1000
                        ? `${node.label} (${(value / 1000).toFixed(1)} kW)`
                        : `${node.label} (${value.toFixed(0)} W)`;
                }}

                // label={(node) => node.label}
                // colors={{ scheme: 'category10' }}
                labelPosition="outside"
                labelOrientation="horizontal"
                nodeOpacity={0.95}
                nodeHoverOthersOpacity={0.35}
                nodeThickness={18}
                nodeInnerPadding={5}
                nodeSpacing={24}
                nodeBorderWidth={0}
                nodeBorderColor={{ from: 'color', modifiers: [['darker', 0.8]] }}
                nodeBorderRadius={3}
                // linkColor="gradient"
                linkOpacity={0.35}
                linkHoverOthersOpacity={0.1}
                linkContract={3}
                enableLinkGradient={true}
                margin={{
                    top: 20,
                    right: 60,
                    bottom: 20,
                    left: 120,
                }}


                colors={(node) => {

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
                }}


            />

        </div>
    );
}
