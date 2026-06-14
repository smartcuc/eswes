/*
# src/hooks/useEnergyFlow.js
*/

import { useEffect, useState } from "react";

export default function useEnergyFlow() {
    const [data, setData] = useState(null);

    useEffect(() => {
        fetch("/api/dashboard/me/")
            .then((res) => res.json())
            .then(setData);
    }, []);

    return data;
}
