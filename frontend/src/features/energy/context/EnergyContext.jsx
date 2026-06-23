/*
# src/features/energy/context/EnergyContext.jsx
*/

import { createContext, useContext, useState, useCallback } from "react";

const EnergyContext = createContext();

export function EnergyProvider({ children }) {
    const [devices, setDevices] = useState({});
    const [history, setHistory] = useState([]);

    const updateMetric = useCallback((event) => {
        const { device_id, value, metric, device_type } = event;

        if (metric !== "power") return;

        // ✅ Geräte State aktualisieren
        setDevices(prev => {
            const updatedDevices = {
                ...prev,
                [device_id]: {
                    ...(prev[device_id] || {}),
                    power: value,
                    type: device_type || prev[device_id]?.type
                }
            };

            // ✅ Gesamtleistung berechnen (für Chart!)
            const totalPower = Object.values(updatedDevices)
                .reduce((sum, d) => sum + (d.power || 0), 0);

            // ✅ HISTORIE aktualisieren
            setHistory(prevHistory => {
                const now = new Date();

                const maxPoints = 50; // ✅ Limit

                const newPoint = {
                    time: now.toLocaleTimeString(),
                    value: totalPower
                };

                const updated = [...prevHistory, newPoint];

                if (updated.length > maxPoints) {
                    return updated.slice(updated.length - maxPoints);
                }

                return updated;
            });

            return updatedDevices;
        });

    }, []);

    return (
        <EnergyContext.Provider value={{ devices, history, updateMetric }}>
            {children}
        </EnergyContext.Provider>
    );
}

export function useEnergy() {
    return useContext(EnergyContext);
}
