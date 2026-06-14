/*
# src/pages/LandingPage.jsx
*/

import { useEffect, useState } from "react";
import Header from "./components/Header";
import EnergyFlow from "./components/EnergyFlow";
import Footer from "./components/Footer";

export default function LandingPage() {
    const [user] = useState(null);

    useEffect(() => {
        document.title = "Sharegy – Energie verstehen & teilen";
    }, []);

    return (
        <div className="min-h-screen bg-gray-50">

            {/* HEADER */}
            <Header user={user} />

            {/* HERO */}
            <section className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white py-28 text-center px-6">
                <h1 className="text-5xl font-bold mb-6">
                    Verstehe deinen Strom. Teile ihn intelligent.
                </h1>

                <p className="max-w-2xl mx-auto text-lg opacity-90">
                    Sharegy zeigt dir, wo deine Energie herkommt, wohin sie geht
                    – und wie du sie optimal nutzt. Für dich allein oder in deiner Community.
                </p>

                <div className="mt-8 flex justify-center gap-4 flex-wrap">
                    <button className="bg-black/30 backdrop-blur px-6 py-3 rounded-lg hover:scale-105 transition">
                        Dashboard ansehen
                    </button>
                    <button className="border border-white px-6 py-3 rounded-lg">
                        Kostenlos starten
                    </button>
                </div>
            </section>

            {/* EMS SECTION */}
            <section className="mt-16 px-6 text-center">
                <h2 className="text-2xl font-semibold mb-6 text-indigo-600">
                    Dein persönliches Energiemanagement
                </h2>

                <p className="text-gray-500 max-w-xl mx-auto mb-10">
                    Behalte Verbrauch, Produktion und Netzbezug jederzeit im Blick.
                    Keine Tabellen – echte Transparenz.
                </p>

                <div className="grid md:grid-cols-3 gap-6 max-w-5xl mx-auto">
                    <div className="bg-white p-6 rounded-xl shadow">
                        <p className="text-lg font-medium">⚡ Live-Verbrauch</p>
                        <p className="text-sm text-gray-500">Was läuft gerade?</p>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow">
                        <p className="text-lg font-medium">☀️ Produktion</p>
                        <p className="text-sm text-gray-500">Was erzeugt deine PV?</p>
                    </div>

                    <div className="bg-white p-6 rounded-xl shadow">
                        <p className="text-lg font-medium">🏠 Netzbezug</p>
                        <p className="text-sm text-gray-500">Was kostet dich Energie?</p>
                    </div>
                </div>
            </section>

            {/* ENERGY FLOW */}
            <section className="mt-20 px-6 text-center">
                <h3 className="text-xl font-semibold mb-6 text-indigo-600">
                    Energie sichtbar machen
                </h3>

                <p className="text-gray-500 max-w-xl mx-auto mb-8">
                    Sieh live, wie Strom zwischen deinem Haushalt, deiner Batterie
                    und dem Netz fließt.
                </p>

                <EnergyFlow />
            </section>

            {/* COMMUNITY */}
            <section className="mt-20 bg-gray-100 py-16 px-6 text-center">
                <div className="max-w-4xl mx-auto">
                    <h2 className="text-2xl font-semibold mb-6">
                        Teile Energie in deiner Community
                    </h2>

                    <p className="text-gray-600 mb-10">
                        Verbinde Haushalte, nutze Überschüsse lokal
                        und reduziere deine Stromkosten.
                    </p>

                    <div className="grid md:grid-cols-3 gap-6">
                        <div className="bg-white p-6 rounded-xl shadow">
                            🤝 Direkt teilen
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow">
                            💶 Fair abrechnen
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow">
                            ⚡ Lokale Optimierung
                        </div>
                    </div>
                </div>
            </section>

            {/* TRUST / VALUE */}
            <section className="mt-20 px-6 text-center">
                <h3 className="text-xl font-semibold mb-6">
                    Warum Sharegy?
                </h3>

                <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto text-left">
                    <div>
                        <h4 className="font-medium">Transparenz</h4>
                        <p className="text-sm text-gray-500">
                            Keine Blackbox. Du siehst jede Bewegung deiner Energie.
                        </p>
                    </div>

                    <div>
                        <h4 className="font-medium">Automatisierung</h4>
                        <p className="text-sm text-gray-500">
                            Optimierung ohne Aufwand – Sharegy regelt das für dich.
                        </p>
                    </div>

                    <div>
                        <h4 className="font-medium">Kosteneffizienz</h4>
                        <p className="text-sm text-gray-500">
                            Nutze mehr deiner eigenen Energie und spare Geld.
                        </p>
                    </div>
                </div>
            </section>

            {/* CTA */}
            <section className="mt-24 bg-black text-white py-20 text-center px-6">
                <h3 className="text-3xl font-semibold mb-4">
                    Starte dein Energy Dashboard
                </h3>

                <p className="text-gray-400 mb-8">
                    In 2 Minuten eingerichtet. Kein Risiko.
                </p>

                <button className="bg-orange-500 hover:bg-orange-600 transition transform hover:scale-105 px-8 py-4 rounded-lg text-lg font-medium">
                    Jetzt kostenlos starten
                </button>
            </section>

            <Footer />
        </div>
    );
}
