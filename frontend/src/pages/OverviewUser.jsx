/*
# src/pages/OverviewUser.jsx
*/

import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function OverviewUser() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function load() {
            try {
                const res = await apiFetch("/api/dashboard/me/");
                const json = await res.json();

                setData(json);
            } catch (e) {
                console.error("Failed to load overview", e);
            } finally {
                setLoading(false);
            }
        }

        load();
    }, []);

    if (loading) {
        return (
            <div className="p-6">
                <p>Lade Daten...</p>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="p-6">
                <h1 className="text-2xl font-bold mb-4">Übersicht</h1>
                <p>Keine Daten vorhanden.</p>
            </div>
        );
    }

    return (
        <div className="p-6 space-y-6">

            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">Übersicht</h1>
                <p className="text-gray-500">
                    Dein Energieverbrauch auf einen Blick
                </p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                <div className="bg-white shadow rounded-lg p-4">
                    <p className="text-gray-500 text-sm">Verbrauch</p>
                    <p className="text-xl font-semibold">
                        {data.consumption_kwh} kWh
                    </p>
                </div>

                <div className="bg-white shadow rounded-lg p-4">
                    <p className="text-gray-500 text-sm">Erzeugung</p>
                    <p className="text-xl font-semibold">
                        {data.generation_kwh} kWh
                    </p>
                </div>

                <div className="bg-white shadow rounded-lg p-4">
                    <p className="text-gray-500 text-sm">Netzbezug</p>
                    <p className="text-xl font-semibold">
                        {data.grid_import_kwh} kWh
                    </p>
                </div>

                <div className="bg-white shadow rounded-lg p-4">
                    <p className="text-gray-500 text-sm">Einspeisung</p>
                    <p className="text-xl font-semibold">
                        {data.grid_export_kwh} kWh
                    </p>
                </div>

            </div>

            {/* CTA wenn keine Daten */}
            {data.consumption_kwh === 0 && (
                <div className="bg-yellow-50 border border-yellow-200 p-4 rounded-lg">
                    <p>
                        Noch keine Daten verfügbar.
                    </p>

                    <button className="mt-3 bg-indigo-600 text-white px-4 py-2 rounded">
                        Zähler hinzufügen
                    </button>
                </div>
            )}

        </div>
    );
}
