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
        <div>
            <div>TEST WITHOUT SANKEY</div>

            {/* optional */}
            <EnergySankey />
        </div>
    );
}

