/*
# src/features/energy/hooks/useEnergyOptimization.js
*/

import { useMemo } from "react";
import { useEnergy } from "../context/EnergyContext";

export default function useEnergyOptimization() {
    const { devices } = useEnergy();

    return useMemo(() => {

        let pv = 0;
        let consumption = 0;
        let battery = 0;

        Object.values(devices).forEach(d => {
            if (!d.power) return;

            if (d.type === "pv") {
                pv += d.power;
            } else if (d.type === "battery") {
                battery += d.power;
            } else {
                consumption += Math.abs(d.power);
            }
        });

        const directUse = Math.min(pv, consumption);

        // ✅ KPIs
        const selfConsumptionRate = pv > 0
            ? (directUse / pv) * 100
            : 0;

        const selfSufficiency = consumption > 0
            ? (directUse / consumption) * 100
            : 0;

        // ✅ Netzbezug
        const gridImport = Math.max(consumption - pv - battery, 0);

        // ✅ Einsparung (Beispiel: 0.30€/kWh)
        const savings =
            (directUse / 1000) * 0.30; // W → kW → €

        return {
            pv,
            consumption,
            battery,
            directUse,
            selfConsumptionRate,
            selfSufficiency,
            gridImport,
            savings
        };

    }, [devices]);
}
