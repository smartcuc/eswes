/*
# src/features/energy/store/useEnergyStore.js
*/

import { useState, useCallback } from "react";

export default function useEnergyStore() {
    const [devices, setDevices] = useState({});

    const updateMetric = useCallback((event) => {
        const { device_id, value, metric } = event;

        if (metric !== "power") return;

        setDevices(prev => ({
            ...prev,
            [device_id]: {
                ...(prev[device_id] || {}),
                power: value
            }
        }));
    }, []);

    return { devices, updateMetric };
}
