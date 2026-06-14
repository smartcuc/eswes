/*
# src/pages/Dashboard.jsx
*/

import { useEffect, useState } from "react";
import EnergyFlow from "../components/EnergyFlow";

export default function Dashboard() {
    const [data, setData] = useState(null);

    useEffect(() => {
        // 👉 später durch echte API ersetzen
        setTimeout(() => {
            setData({
                consumption: 2.4,
                production: 3.8,
                grid: 0.6,
                selfUsage: 84,
                trend: "good"
            });
        }, 500);
    }, []);

    if (!data) {
        return (
            <div className="min-h-screen flex items-center justify-center text-gray-500">
                Daten werden geladen...
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gray-50 p-6">

            <div className="max-w-6xl mx-auto">

                {/* HEADER */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold">
                        Dein Energy Dashboard ⚡
                    </h1>
                    <p className="text-gray-500">
                        Live-Überblick über deine Energie
                    </p>
                </div>

                {/* FLOW */}
                <div className="bg-white p-6 rounded-2xl shadow mb-10">
                    <h2 className="text-lg font-semibold mb-4">
                        Energiefluss jetzt
                    </h2>

                    <EnergyFlow />
                </div>

                {/* STATS */}
                <div className="grid md:grid-cols-3 gap-6 mb-10">

                    <StatCard
                        label="Verbrauch"
                        value={data.consumption}
                        color="indigo"
                        trend="+0.2 kWh"
                    />

                    <StatCard
                        label="Produktion"
                        value={data.production}
                        color="orange"
                        trend="+1.1 kWh"
                    />

                    <StatCard
                        label="Netzbezug"
                        value={data.grid}
                        color="gray"
                        trend="-0.5 kWh"
                    />

                </div>

                {/* INSIGHT */}
                <div className="bg-indigo-50 border border-indigo-100 p-5 rounded-xl mb-10">

                    <p className="text-indigo-700 font-medium text-lg">
                        💡 Du nutzt {data.selfUsage}% deiner Energie selbst
                    </p>

                    <p className="text-sm text-indigo-600 mt-1">
                        {data.trend === "good"
                            ? "Sehr gut – du reduzierst deinen Netzbezug."
                            : "Potenzial zur Optimierung vorhanden."}
                    </p>
                </div>

                {/* COMMUNITY CTA */}
                <div className="bg-white p-6 rounded-2xl shadow text-center">

                    <h3 className="text-lg font-semibold mb-2">
                        Mehr aus deiner Energie holen
                    </h3>

                    <p className="text-gray-500 text-sm mb-4">
                        Teile Energie mit anderen oder optimiere gemeinsam.
                    </p>

                    <div className="flex flex-col sm:flex-row gap-3 justify-center">
                        <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-3 rounded-lg">
                            Community erstellen
                        </button>

                        <button className="border border-gray-300 px-5 py-3 rounded-lg">
                            Einladung eingeben
                        </button>
                    </div>
                </div>

            </div>
        </div>
    );
}


function StatCard({ label, value, color, trend }) {
    const colorMap = {
        indigo: "text-indigo-600",
        orange: "text-orange-500",
        gray: "text-gray-700"
    };

    return (
        <div className="bg-white p-5 rounded-xl shadow text-center">

            <p className="text-sm text-gray-500 mb-1">{label}</p>

            <p className={`text-2xl font-bold ${colorMap[color]}`}>
                {value} kWh
            </p>

            <p className="text-xs text-gray-400 mt-1">
                {trend}
            </p>

        </div>
    );
}
