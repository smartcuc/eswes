/*
# LandingPage.jsx
*/

import Header from "./Header";
import EnergyFlow from "./EnergyFlow";

export default function LandingPage() {
    return (
        <div className="min-h-screen bg-gray-50">

            <Header />

            {/* HERO */}
            <section className="bg-gradient-to-r from-orange-400 via-pink-500 to-indigo-600 text-white py-24 text-center">
                <h1 className="text-4xl font-bold mb-4">
                    Energie gemeinsam nutzen
                </h1>

                <p className="max-w-xl mx-auto text-lg">
                    Sharegy verbindet Nachbarschaften und macht Energie sichtbar.
                </p>
            </section>

            {/* STATS */}
            <div className="mt-10 max-w-4xl mx-auto grid grid-cols-3 gap-6 px-6">
                <div className="bg-white p-6 rounded-xl shadow text-center">
                    <p className="text-2xl font-bold text-orange-500">12 kWh</p>
                    <p className="text-gray-500 text-sm">geteilt heute</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow text-center">
                    <p className="text-2xl font-bold text-indigo-500">8</p>
                    <p className="text-gray-500 text-sm">Haushalte</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow text-center">
                    <p className="text-2xl font-bold text-pink-500">92%</p>
                    <p className="text-gray-500 text-sm">lokal genutzt</p>
                </div>
            </div>

            {/* FLOW */}
            <div className="mt-12">
                <EnergyFlow />
            </div>

        </div>
    );
}
