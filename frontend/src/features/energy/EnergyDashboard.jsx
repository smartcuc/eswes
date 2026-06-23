/*
# src/features/energy/EnergyDashboard.jsx
*/

import EnergySankey from "./components/EnergySankey";
import EnergyChart from "./components/EnergyChart";
import useEnergyInsights from "./hooks/useEnergyInsights";
import useEnergyOptimization from "./hooks/useEnergyOptimization";

export default function EnergyDashboard() {
    // ✅ hooks IMMER oben
    const insights = useEnergyInsights();
    const opt = useEnergyOptimization();

    return (
        <div style={{ padding: 20 }}>

            {/* ✅ HEADER */}
            <h2 style={{ marginBottom: 10 }}>⚡ Energy Dashboard</h2>

            {/* ✅ KPI SECTION */}
            <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
                <div>PV: {opt.pv.toFixed(0)} W</div>
                <div>Verbrauch: {opt.consumption.toFixed(0)} W</div>
                <div>Batterie: {opt.battery.toFixed(0)} W</div>
            </div>

            <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
                <div>Eigenverbrauch: {opt.selfConsumptionRate.toFixed(0)}%</div>
                <div>Autarkie: {opt.selfSufficiency.toFixed(0)}%</div>
                <div>Ersparnis: {opt.savings.toFixed(2)} €</div>
            </div>

            {/* ✅ INSIGHTS */}
            <div style={{ marginBottom: 20 }}>
                {insights.map((text, i) => (
                    <div key={i}>{text}</div>
                ))}
            </div>

            {/* ✅ SANKEY */}
            <div style={{ marginBottom: 40 }}>
                <EnergySankey />
            </div>

            {/* ✅ CHART */}
            <div>
                <EnergyChart />
            </div>

        </div>
    );
}


function Card({ title, children }) {
    return (
        <div style={{
            flex: 1,
            padding: 20,
            background: "#111",
            color: "#fff",
            borderRadius: 10
        }}>
            <div style={{ fontSize: 12, color: "#aaa" }}>{title}</div>
            <div style={{ fontSize: 24 }}>{children}</div>
        </div>
    );
}
