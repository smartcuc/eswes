/*
# src/features/energy/EnergyDashboard.jsx
*/

import EnergySankey from "./components/EnergySankey";
import EnergyChart from "./components/EnergyChart";
import useEnergyInsights from "./hooks/useEnergyInsights";
import useEnergyOptimization from "./hooks/useEnergyOptimization";

export default function EnergyDashboard() {

    const insights = useEnergyInsights();
    const opt = useEnergyOptimization();

    return (
        <div style={{ padding: 20 }}>
            <h1>⚡ Energy Dashboard</h1>

            {/* ✅ INSIGHTS */}
            <div style={{ marginBottom: 20 }}>
                {insights.map((text, i) => (
                    <div key={i} className="text-green-400 text-sm">
                        {text}
                    </div>
                ))}
            </div>

            {/* ✅ KPI */}
            <div style={{ display: "flex", gap: 20, marginBottom: 20 }}>
                <Card title="Eigenverbrauch">
                    {opt.selfConsumptionRate.toFixed(0)} %
                </Card>

                <Card title="Autarkie">
                    {opt.selfSufficiency.toFixed(0)} %
                </Card>

                <Card title="Ersparnis">
                    {opt.savings.toFixed(2)} €
                </Card>
            </div>

            {/* ✅ SANKEY */}
            <EnergySankey />

            {/* ✅ CHART optional */}
            <div style={{ marginTop: 30 }}>
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
