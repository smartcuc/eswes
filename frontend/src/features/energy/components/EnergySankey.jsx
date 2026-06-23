/*
# src/features/energy/components/EnergySankey.jsx
*/

import { ResponsiveSankey } from "@nivo/sankey";
import { useMemo, useState } from "react";
import useEnergySocket from "../hooks/useEnergySocket";
import { useEnergy } from "../context/EnergyContext";

export default function EnergySankey() {
    const { devices, updateMetric } = useEnergy();

    const [grouped, setGrouped] = useState(true);

    // ✅ WebSocket → global store
    useEnergySocket(updateMetric);

    const data = useMemo(() => {

        const nodes = [];
        const links = [];

        const HOUSE = "house";

        if (grouped) {
            // =========================
            // ✅ GROUPED MODE
            // =========================

            let pv = 0;
            let battery = 0;
            let consumption = 0;

            Object.values(devices).forEach(d => {
                if (!d.power) return;

                if (d.type === "pv") pv += d.power;
                else if (d.type === "battery") battery += d.power;
                else consumption += Math.abs(d.power);
            });

            nodes.push(
                { id: "pv", label: "PV" },
                { id: "battery", label: "Batterie" },
                { id: HOUSE, label: "Haus" },
                { id: "consumer", label: "Verbraucher" }
            );

            if (pv > 0)
                links.push({ source: "pv", target: HOUSE, value: pv });

            if (battery > 0)
                links.push({ source: "battery", target: HOUSE, value: battery });

            if (consumption > 0)
                links.push({ source: HOUSE, target: "consumer", value: consumption });

        } else {
            // =========================
            // ✅ DEVICE MODE
            // =========================

            nodes.push({ id: HOUSE, label: "Haus" });

            Object.entries(devices).forEach(([id, d]) => {
                if (!d.power) return;

                const nodeId = `device_${id}`;

                nodes.push({
                    id: nodeId,
                    label: d.type || `Device ${id}`
                });

                if (d.type === "pv") {
                    links.push({
                        source: nodeId,
                        target: HOUSE,
                        value: d.power
                    });
                } else if (d.type === "battery" && d.power > 0) {
                    links.push({
                        source: nodeId,
                        target: HOUSE,
                        value: d.power
                    });
                } else {
                    links.push({
                        source: HOUSE,
                        target: nodeId,
                        value: Math.abs(d.power)
                    });
                }
            });
        }

        return { nodes, links };

    }, [devices, grouped]);

    if (!Object.keys(devices).length) {
        return <div className="text-gray-400">Warte auf Live-Daten…</div>;
    }

    return (
        <div>
            {/* ✅ TOGGLE */}
            <div style={{ marginBottom: 10 }}>
                <button onClick={() => setGrouped(true)}>Grouped</button>
                <button onClick={() => setGrouped(false)}>Devices</button>
            </div>

            <div style={{ height: 500 }}>
                <ResponsiveSankey
                    data={data}
                    nodeThickness={20}
                    nodeSpacing={24}
                    animate={true}
                    motionConfig="gentle"
                    colors={(node) => {
                        if (node.id === "pv") return "#f59e0b";
                        if (node.id === "battery") return "#10b981";
                        if (node.id === "house") return "#3b82f6";
                        return "#ef4444";
                    }}
                />
            </div>
        </div>
    );
}
