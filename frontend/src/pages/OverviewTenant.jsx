/*
# src/pages/OverviewTenant.jsx
*/

import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function OverviewTenant() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const res = await apiFetch("/api/dashboard/me/");
                const json = await res.json();

                setData(json);
            } catch (e) {
                console.error("Failed to load tenant overview", e);
            } finally {
                setLoading(false);
            }
        }

        load();
    }, []);

    if (loading) {
        return <div className="p-6">Lade Community Daten...</div>;
    }

    return (
        <div className="p-6 space-y-6">

            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">
                    Community Übersicht
                </h1>
                <p className="text-gray-500">
                    Energie innerhalb deiner Community
                </p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                <div className="bg-white shadow rounded-lg p-4">
                    <p className="text-gray-500 text-sm">
                        Gesamtverbrauch
                    </p>
                    <p className="text-xl font-semibold">
                        {data?.consumption_kwh} kWh
                    </p>
                </div>

                <div className="bg-white shadow rounded-lg p-4">
                    <p className="text-gray-500 text-sm">
                        Erzeugung
                    </p>
                    <p className="text-xl font-semibold">
                        {data?.generation_kwh} kWh
                    </p>
                </div>

            </div>

            {/* Zusatz für Community */}
            <div className="bg-indigo-50 p-4 rounded-lg">
                <p className="font-medium">
                    👥 Community aktiv
                </p>
                <p className="text-sm text-gray-600">
                    Du bist Teil einer Energie-Gemeinschaft
                </p>
            </div>

        </div>
    );
}
