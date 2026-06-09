/*
# src/pages/LandingPage.jsx
*/

import { useState, useEffect } from "react";
import { useUser } from "./hooks/useUser";

import Header from "./components/Header";
import EnergyFlow from "./components/EnergyFlow";
import Footer from "./components/Footer";

import Impressum from "./pages/Impressum";
import Datenschutz from "./pages/Datenschutz";


export default function LandingPage() {

    const [showImpressum, setShowImpressum] = useState(false);
    const [showDatenschutz, setShowDatenschutz] = useState(false);
    const user = useUser();


    useEffect(() => {
        document.title = "Sharegy – Energie gemeinsam nutzen";
    }, []);


    return (
        <div className="min-h-screen bg-gray-50">

            {/* HEADER */}
            <Header user={user} />

            {/* HERO */}
            <section className="bg-gradient-to-r from-orange-400 via-pink-500 to-indigo-600 text-white py-28 text-center px-6">
                <h1 className="text-5xl font-bold mb-6">
                    Energie gemeinsam nutzen – lokal & transparent
                </h1>

                <p className="max-w-2xl mx-auto text-lg opacity-90">
                    Sharegy verbindet Haushalte, visualisiert Energieflüsse
                    und ermöglicht faires Energy Sharing in deiner Community.
                </p>

                <div className="mt-8 flex justify-center gap-4 flex-wrap">
                    <button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition">
                        Demo ansehen
                    </button>

                    <button className="border border-white px-6 py-3 rounded-lg">
                        Community starten
                    </button>
                </div>
            </section>

            {/* STATS */}
            <section className="mt-12 max-w-5xl mx-auto grid grid-cols-1 md:grid-cols-3 gap-6 px-6">
                <div className="bg-white p-6 rounded-xl shadow text-center">
                    <p className="text-2xl font-bold text-orange-500">12 kWh</p>
                    <p className="text-gray-500 text-sm">heute geteilt</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow text-center">
                    <p className="text-2xl font-bold text-indigo-500">8</p>
                    <p className="text-gray-500 text-sm">Haushalte verbunden</p>
                </div>

                <div className="bg-white p-6 rounded-xl shadow text-center">
                    <p className="text-2xl font-bold text-pink-500">92%</p>
                    <p className="text-gray-500 text-sm">lokal genutzt</p>
                </div>
            </section>

            {/* ENERGY FLOW (USP) */}
            <section className="mt-16 px-6 text-center">
                <h3 className="text-xl font-semibold mb-8 text-indigo-600">
                    Sieh, wie Energie wirklich fließt
                </h3>

                <p className="text-gray-500 max-w-xl mx-auto mb-6">
                    Keine Tabellen. Keine Blackbox.
                    Sharegy zeigt dir live, wie Strom zwischen Teilnehmern verteilt wird.
                </p>

                <EnergyFlow
                    data={{
                        endpoint: "/api/v1/energy-flow/solar-gmbh/"
                    }}
                />
            </section>

            {/* FEATURES */}
            <section className="mt-16 px-6">
                <div className="max-w-6xl mx-auto">

                    <h2 className="text-2xl font-semibold text-center mb-10">
                        Alles für deine Energy Community
                    </h2>

                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">

                        <div className="bg-white p-6 rounded-xl shadow transition transform hover:-translate-y-1 hover:shadow-lg">
                            <h3 className="font-medium mb-2 text-indigo-600">
                                🔋 Energiemanagement
                            </h3>

                            <p className="text-gray-500 text-sm">
                                Live-Verbrauch, Produktion und Speicher – alles auf einen Blick.
                            </p>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow transition transform hover:-translate-y-1 hover:shadow-lg">
                            <h3 className="font-medium mb-2 text-orange-500">
                                🤝 Community Sharing
                            </h3>
                            <p className="text-gray-500 text-sm">
                                Teile Energie direkt innerhalb deiner Nachbarschaft.
                            </p>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow transition transform hover:-translate-y-1 hover:shadow-lg">
                            <h3 className="font-medium mb-2 text-emerald-600">
                                💶 Automatische Abrechnung
                            </h3>
                            <p className="text-gray-500 text-sm">
                                Verbrauch und Kosten werden fair und transparent verteilt.
                            </p>
                        </div>

                        <div className="bg-white p-6 rounded-xl shadow transition transform hover:-translate-y-1 hover:shadow-lg">
                            <h3 className="font-medium mb-2 text-indigo-600">
                                📊 Messen & Verstehen
                            </h3>
                            <p className="text-gray-500 text-sm">
                                Visualisierung statt Tabellen – verstehe deine Energie sofort.
                            </p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow transition transform hover:-translate-y-1 hover:shadow-lg">
                            <h3 className="font-medium mb-2 text-orange-500">
                                🌐 Plattform
                            </h3>
                            <p className="text-gray-500 text-sm">
                                Multi-Tenant Architektur für beliebige Communities.
                            </p>
                        </div>
                        <div className="bg-white p-6 rounded-xl shadow transition transform hover:-translate-y-1 hover:shadow-lg">
                            <h3 className="font-medium mb-2 text-emerald-600">
                                ⚡ Tarife & Netz
                            </h3>
                            <p className="text-gray-500 text-sm">
                                Integration von Stromtarifen und Netzbezug.
                            </p>
                        </div>
                    </div>
                </div >
            </section >

            {/* HOW IT WORKS */}
            <section section className="mt-16 bg-gray-100 py-16 px-6" >
                <div className="max-w-4xl mx-auto text-center">

                    <h3 className="text-xl font-semibold mb-8">
                        So funktioniert Energy Sharing
                    </h3>

                    <div className="space-y-3 text-gray-700 text-left max-w-xl mx-auto">
                        <p>1. Energie wird lokal erzeugt oder verbraucht</p>
                        <p>2. Sharegy verteilt Strom automatisch innerhalb der Community</p>
                        <p>3. Überschüsse werden gespeichert oder ins Netz eingespeist</p>
                        <p>4. Kosten und Erträge werden transparent verrechnet</p>
                    </div>

                </div>
            </section >

            {/* CTA */}
            <section section className="mt-20 bg-black text-white py-20 text-center px-6" >
                <h3 className="text-2xl font-semibold mb-4">
                    Starte deine Energy Community
                </h3>

                <p className="text-gray-300 mb-6">
                    Einfach. Transparent. Lokal.
                </p>
                <button className="bg-orange-500 hover:bg-orange-600 transition transform hover:scale-105 text-white px-8 py-4 rounded-lg unded-lg text-lg font-medium">
                    Jetzt starten
                </button>
            </section >

            <Footer
                onOpenImpressum={() => setShowImpressum(true)}
                onOpenDatenschutz={() => setShowDatenschutz(true)}
            />
            {
                showImpressum && (
                    <Impressum onClose={() => setShowImpressum(false)} />
                )
            }

            {
                showDatenschutz && (
                    <Datenschutz onClose={() => setShowDatenschutz(false)} />
                )
            }

        </div >
    );
}

