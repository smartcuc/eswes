/*
# TenantPage.jsx
*/

import { Link } from "react-router-dom";

import Sidebar from "./Sidebar";
import EnergyFlow from "./EnergyFlow";

/* HERO */
function Hero() {
    return (
        <div className="mb-8">
            <h1 className="text-3xl font-bold">
                Dashboard
            </h1>
            <p className="text-gray-600">
                Überblick deiner Energie-Community
            </p>

            <Link to="/dashboard">
                <button className="mt-6 px-8 py-4 bg-white text-black rounded-xl shadow">
                    Dashboard öffnen
                </button>
            </Link>

        </div>


    );
}

/* STATS */
function Stats() {
    return (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">

            <div className="bg-white p-6 rounded-xl shadow">
                <p className="text-2xl font-bold text-orange-500">12 kWh</p>
                <p className="text-gray-500 text-sm">geteilt heute</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow">
                <p className="text-2xl font-bold text-indigo-500">8</p>
                <p className="text-gray-500 text-sm">Haushalte</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow">
                <p className="text-2xl font-bold text-pink-500">92%</p>
                <p className="text-gray-500 text-sm">lokale Nutzung</p>
            </div>

        </div>
    );
}

export default function TenantPage() {
    return (
        <div className="flex h-screen bg-gray-50">

            {/* ✅ Sidebar FIX */}
            <Sidebar />

            {/* ✅ Content Bereich */}
            <main className="flex-1 overflow-y-auto p-10">

                <Hero />

                <Stats />

                <EnergyFlow />

            </main>

        </div>
    );
}
