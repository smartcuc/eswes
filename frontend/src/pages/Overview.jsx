/*
# src/pages/Overview.jsx
*/

import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import OverviewLayout from "../components/overview/OverviewLayout";

export default function Overview() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const res = await apiFetch("/api/dashboard/me/");

                if (!res.ok) throw new Error("Dashboard failed");

                const json = await res.json();

                setData(json);
            } catch (e) {
                console.error("Overview load failed", e);
            } finally {
                setLoading(false);
            }
        }

        load();
    }, []);

    return (
        <OverviewLayout
            data={data}
            loading={loading}
        />
    );
}
