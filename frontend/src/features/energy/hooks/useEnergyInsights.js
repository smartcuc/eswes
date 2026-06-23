/*
#
*/

import { useMemo } from "react";
import { useEnergy } from "../context/EnergyContext";

export default function useEnergyInsights() {
    const { devices } = useEnergy();

    return useMemo(() => {
        let pv = 0;
        let consumption = 0;
        let battery = 0;

        Object.values(devices).forEach(d => {
            if (!d.power) return;

            if (d.type === "pv") pv += d.power;
            else if (d.type === "battery") battery += d.power;
            else consumption += Math.abs(d.power);
        });

        const directUse = Math.min(pv, consumption);
        const selfConsumptionRate = pv > 0 ? (directUse / pv) * 100 : 0;

        const insights = [];

        if (selfConsumptionRate > 0) {
            insights.push(`⚡ ${selfConsumptionRate.toFixed(0)}% deiner PV wird direkt genutzt`);
        }

        if (battery > 0) {
            insights.push("🔋 Batterie entlädt");
        }
        if (battery < 0) {
            insights.push("🔋 Batterie lädt");
        }

        if (pv > consumption) {
            insights.push("🌍 Überschussenergie vorhanden");
        }

        return insights;

    }, [devices]);
}
