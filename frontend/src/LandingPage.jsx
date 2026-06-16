/*
# src/pages/LandingPage.jsx
*/

import { useEffect, useState } from "react";
import { useUser } from "./hooks/useUser";

import Header from "./components/Header";
import EnergyFlow from "./components/EnergyFlow";
import Footer from "./components/Footer";

import { trackEvent } from "./lib/track";

export default function LandingPage() {

    const { user } = useUser();
    const [variant] = useState(Math.random() > 0.5 ? "A" : "B");

    useEffect(() => {
        document.title = "Sharegy – Dein Energy OS";
        trackEvent("landing_view", { variant });
    }, [variant]);

    const handleStart = () => {
        trackEvent("cta_click", {
            location: "hero_primary",
            variant
        });

        window.location.href = "/login";
    };

    return (
        <div className="min-h-screen bg-gray-50">

            <Header user={user} />

            {/* 🔥 HERO */}
            <section className="relative bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white py-28 text-center px-6 overflow-hidden">

                <div className="absolute inset-0 bg-white/5 blur-3xl opacity-30" />

                <h1 className="text-5xl font-bold mb-6 leading-tight relative z-10">
                    {
                        variant === "A"
                            ? "Dein Strom kostet dich zu viel – obwohl genug da ist"
                            : "Du nutzt deine Energie nicht optimal – Sharegy ändert das"
                    }
                </h1>

                <p className="max-w-2xl mx-auto text-lg opacity-90 relative z-10">
                    Verstehe, wohin dein Strom geht, optimiere automatisch
                    und teile Energie lokal mit deiner Community – alles in einer Plattform.
                </p>

                <div className="mt-8 flex justify-center gap-4 flex-wrap relative z-10">

                    {/* ✅ LIVE VIEW (Scroll) */}
                    <button
                        onClick={() => {
                            trackEvent("cta_click", {
                                location: "hero_secondary",
                                variant
                            });

                            document
                                .getElementById("energy-flow")
                                ?.scrollIntoView({ behavior: "smooth" });
                        }}
                        className="bg-black/30 backdrop-blur px-6 py-3 rounded-lg hover:scale-105 transition"
                    >
                        Live ansehen
                    </button>

                    {/* ✅ MAIN CTA (konsistent) */}
                    <button
                        onClick={handleStart}
                        className="border border-white px-6 py-3 rounded-lg hover:scale-105 transition"
                    >
                        Jetzt kostenlos starten →
                    </button>

                </div>

                {/* ✅ TRUST BOOST */}
                <div className="mt-6 text-sm opacity-80">
                    Kein Setup · Kein Risiko · Funktioniert sofort
                </div>

            </section>

            {/* TRUST */}
            <section className="mt-10 text-center px-6">

                <div className="text-sm text-gray-500">
                    Für Haushalte & Energie-Communities entwickelt
                </div>

                <div className="flex justify-center gap-8 mt-4 text-gray-400 text-sm">
                    <span>⚡ PV & Smart Meter</span>
                    <span>🏘️ Communities</span>
                    <span>🔌 Energy Sharing</span>
                </div>

            </section>

            {/* CORE */}
            <section className="mt-16 text-center px-6">

                <h2 className="text-2xl font-semibold mb-4 text-indigo-600">
                    Ein System für deine Energie
                </h2>

                <p className="text-gray-500 max-w-xl mx-auto">
                    Verstehen, steuern und teilen – alles an einem Ort.
                </p>

            </section>

            {/* SPLIT */}
            <section className="mt-12 max-w-6xl mx-auto grid md:grid-cols-2 gap-8 px-6">

                <div className="bg-white p-8 rounded-2xl shadow hover:shadow-lg transition">
                    <h3 className="text-lg font-semibold mb-4 text-indigo-600">
                        ⚡ Für dein Zuhause
                    </h3>

                    <p className="text-gray-500 text-sm mb-6">
                        Behalte deinen Verbrauch im Blick und optimiere automatisch.
                    </p>

                    <ul className="space-y-2 text-sm text-gray-600">
                        <li>✅ Live-Verbrauch</li>
                        <li>✅ Produktion sichtbar</li>
                        <li>✅ Kosten reduzieren</li>
                    </ul>
                </div>

                <div className="bg-white p-8 rounded-2xl shadow hover:shadow-lg transition">
                    <h3 className="text-lg font-semibold mb-4 text-orange-500">
                        🤝 Für deine Community
                    </h3>

                    <p className="text-gray-500 text-sm mb-6">
                        Teile Energie und nutze Überschüsse lokal.
                    </p>

                    <ul className="space-y-2 text-sm text-gray-600">
                        <li>✅ Energie teilen</li>
                        <li>✅ Fair abrechnen</li>
                        <li>✅ Gemeinsam sparen</li>
                    </ul>
                </div>

            </section>

            {/* MID CTA */}
            <div className="mt-12 text-center">

                <button
                    onClick={() =>
                        trackEvent("cta_click", {
                            location: "mid",
                            variant
                        })
                    }
                    className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg transition transform hover:scale-105"
                >
                    Jetzt kostenlos starten →
                </button>

            </div>

            {/* ✅ ENERGY FLOW */}
            <section id="energy-flow" className="mt-20 px-6 text-center">

                <h3 className="text-xl font-semibold mb-4 text-indigo-600">
                    So fließt Energie in deiner Community
                </h3>

                <p className="text-gray-500 max-w-xl mx-auto mb-8">
                    In Echtzeit sichtbar: Verbrauch, Produktion und Sharing.
                </p>

                {/* ✅ Demo Mode = immer sichtbar */}
                <EnergyFlow mode="demo" />

            </section>

            {/* ✅ GROWTH HOOK */}
            <section className="mt-20 bg-gray-100 py-16 px-6 text-center">

                <h3 className="text-xl font-semibold mb-4">
                    Mehr Wert durch deine Community
                </h3>

                <p className="text-gray-600 max-w-xl mx-auto">
                    Je mehr teilnehmen, desto mehr Energie bleibt lokal –
                    und desto geringer werden deine Kosten.
                </p>

                {/* ✅ Growth CTA */}
                <div className="mt-4">
                    <button className="text-sm text-indigo-600 hover:underline">
                        Community erstellen →
                    </button>
                </div>

            </section>

            {/* FINAL CTA */}
            <section className="mt-24 bg-black text-white py-20 text-center px-6">

                <h3 className="text-3xl font-semibold mb-4">
                    Starte jetzt – in unter 2 Minuten
                </h3>

                <p className="text-gray-400 mb-8">
                    Keine Installation. Kein Risiko.
                </p>

                <button
                    onClick={() =>
                        trackEvent("cta_click", {
                            location: "final",
                            variant
                        })
                    }
                    className="bg-orange-500 hover:bg-orange-600 transition transform hover:scale-105 px-8 py-4 rounded-lg text-lg font-medium"
                >
                    Jetzt kostenlos starten
                </button>

            </section>

            <Footer />

        </div>
    );
}
