/*
# src/hooks/useEnergyFlow.js
*/

import { useEffect, useState } from "react";

export default function useEnergyFlow() {
    const [data, setData] = useState(null);

    useEffect(() => {
        const load = () => {
            fetch("/api/energy/fake-dashboard/")
                .then((res) => res.json())
                .then(setData);
        };

        load();

        const interval = setInterval(load, 2000); // alle 2s neue Daten

        return () => clearInterval(interval);
    }, []);

    return data;
}
