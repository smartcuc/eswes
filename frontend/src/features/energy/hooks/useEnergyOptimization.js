/*
# src/features/energy/hooks/useEnergyOptimization.js
*/

import { useMemo } from "react";
import { useEnergy } from "../context/EnergyContext";

export default function useEnergyOptimization() {
    const energy = useEnergy();

    return useMemo(() => {

        // ✅ SAFETY GUARD
        if (!energy || !energy.devices) {
            return {
                pv: 0,
                consumption: 0,
                battery: 0,
                directUse: 0,
                selfConsumptionRate: 0,
                selfSufficiency: 0,
                gridImport: 0,
                savings: 0
            };
        }

        const { devices } = energy;

        let pv = 0;
        let consumption = 0;
        let battery = 0;

        Object.values(devices).forEach(d => {
            if (!d?.power) return;

            if (d.type === "pv") {
                pv += d.power;
            } else if (d.type === "battery") {
                battery += d.power;
            } else {
                consumption += Math.abs(d.power);
            }
        });

        const directUse = Math.min(pv, consumption);

        const selfConsumptionRate =
            pv > 0 ? (directUse / pv) * 100 : 0;

        const selfSufficiency =
            consumption > 0 ? (directUse / consumption) * 100 : 0;

        const gridImport = Math.max(
            consumption - pv - battery,
            0
        );

        const savings = (directUse / 1000) * 0.30;

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

    }, [energy]);
}