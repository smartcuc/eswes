/*
# src/components/EnergyFlow.jsx
*/

import useEnergyFlow from "../hooks/useEnergyFlow";

export default function EnergyFlow() {
    const data = useEnergyFlow();

    if (!data) {
        return <div className="text-gray-400">Lade Energiefluss...</div>;
    }

    const { flow } = data;

    return (
        <div className="grid grid-cols-3 gap-10 text-center items-center">

            {/* PV */}
            <div>
                <div className="text-yellow-500 text-3xl">☀️</div>
                <div className="mt-2 text-sm text-gray-600">PV</div>

                <FlowValue value={flow.pv_to_load} label="→ Haus" />
                <FlowValue value={flow.pv_to_battery} label="→ Batterie" />
                <FlowValue value={flow.pv_to_grid} label="→ Netz" />
            </div>

            {/* HOUSE */}
            <div>
                <div className="text-3xl">🏠</div>
                <div className="mt-2 text-sm text-gray-600">Haus</div>

                <FlowValue value={flow.battery_to_load} label="← Batterie" />
                <FlowValue value={flow.grid_to_load} label="← Netz" />
            </div>

            {/* BATTERY + GRID */}
            <div className="space-y-6">

                {/* BATTERY */}
                <div>
                    <div className="text-green-600 text-3xl">🔋</div>
                    <div className="text-sm text-gray-600">Batterie</div>
                </div>

                {/* GRID */}
                <div>
                    <div className="text-blue-500 text-3xl">⚡</div>
                    <div className="text-sm text-gray-600">Netz</div>
                </div>

            </div>

        </div>
    );
}

function FlowValue({ value, label }) {
    if (!value || value <= 0) return null;

    return (
        <div className="text-sm mt-1 text-gray-500">
            {label}: {value.toFixed(1)} kW
        </div>
    );
}
