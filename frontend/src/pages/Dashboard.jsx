/*
# src/pages/Dashboard.jsx
*/

import EnergyFlow from "../components/EnergyFlow";

export default function Overview() {

    const hasData = false; // 🔥 später dynamisch machen

    return (
        <div className="min-h-screen bg-gray-50 p-6">

            <div className="max-w-6xl mx-auto">

                {/* HEADER */}
                <div className="mb-8">
                    <h1 className="text-2xl font-bold">
                        Dein Energy Dashboard ⚡
                    </h1>
                    <p className="text-gray-500">
                        Dein persönlicher Überblick über Energieflüsse
                    </p>
                </div>

                {!hasData ? (
                    <>
                        {/* EMPTY STATE */}
                        <div className="bg-white p-8 rounded-2xl shadow mb-10 text-center">

                            <h2 className="text-xl font-semibold mb-2">
                                Dein Dashboard ist bereit 🚀
                            </h2>

                            <p className="text-gray-500 mb-6">
                                Aktuell sind noch keine Energiedaten verfügbar.
                                Sobald Daten vorliegen, siehst du hier deinen Energiefluss in Echtzeit.
                            </p>

                            <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-600">
                                💡 Du kannst Sharegy bereits jetzt verstehen und erkunden – unten siehst du eine Beispielansicht.
                            </div>
                        </div>

                        {/* PREVIEW FLOW */}
                        <div className="bg-white p-6 rounded-2xl shadow mb-10">

                            <h3 className="text-lg font-semibold mb-2">
                                So sieht dein Energiefluss aus
                            </h3>

                            <p className="text-sm text-gray-500 mb-6">
                                Vorschau auf dein zukünftiges Dashboard
                            </p>

                            <EnergyFlow />
                        </div>

                        {/* VALUE SECTION */}
                        <div className="bg-indigo-50 border border-indigo-100 p-6 rounded-xl text-center">

                            <h4 className="font-semibold text-indigo-700 mb-2">
                                Was du hier bald sehen wirst
                            </h4>

                            <div className="text-sm text-indigo-600 space-y-2">
                                <p>⚡ Wie viel Energie du verbrauchst</p>
                                <p>☀️ Wie viel du selbst produzierst</p>
                                <p>🏠 Wann du Strom aus dem Netz beziehst</p>
                            </div>

                        </div>
                    </>
                ) : (
                    <>
                        {/* ✅ SPÄTER: echtes Dashboard hier */}
                        <div className="bg-white p-6 rounded shadow">
                            echte daten kommen hier rein
                        </div>
                    </>
                )}

            </div>
        </div>
    );
}
