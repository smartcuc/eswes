/*
# src/pages/Onboarding.jsx
*/

import { useState } from "react";
import { useNavigate } from "react-router-dom";

export default function Onboarding() {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-6">

            <div className="bg-white w-full max-w-xl rounded-2xl shadow-xl p-8">

                {/* STEP INDICATOR */}
                <div className="text-sm text-gray-400 mb-4 text-center">
                    Schritt {step} von 3
                </div>

                {/* STEP 1 */}
                {step === 1 && (
                    <>
                        <h1 className="text-2xl font-bold text-center mb-4">
                            Willkommen bei Sharegy ⚡
                        </h1>

                        <p className="text-gray-500 text-center mb-6">
                            Lass uns dein persönliches Energy Dashboard einrichten.
                        </p>

                        <div className="space-y-3 text-gray-700 text-sm">
                            <p>✅ Verstehe deinen Stromverbrauch</p>
                            <p>✅ Sieh deine Produktion in Echtzeit</p>
                            <p>✅ Nutze Energy Sharing in deiner Community</p>
                        </div>

                        <button
                            onClick={() => setStep(2)}
                            className="mt-8 w-full bg-indigo-600 text-white py-3 rounded-lg"
                        >
                            Los geht’s
                        </button>
                    </>
                )}

                {/* STEP 2 */}
                {step === 2 && (
                    <>
                        <h2 className="text-xl font-semibold text-center mb-4">
                            Dein Setup
                        </h2>

                        <p className="text-gray-500 text-center mb-6">
                            Was möchtest du zuerst tun?
                        </p>

                        <div className="space-y-4">

                            <button
                                onClick={() => setStep(3)}
                                className="w-full p-4 border rounded-lg hover:bg-gray-50 text-left"
                            >
                                ⚡ Nur mein Energiemanagement nutzen
                                <div className="text-xs text-gray-500">
                                    Perfekt für Einzel-Nutzer
                                </div>
                            </button>

                            <button
                                onClick={() => setStep(3)}
                                className="w-full p-4 border rounded-lg hover:bg-gray-50 text-left"
                            >
                                🤝 Energy Sharing starten
                                <div className="text-xs text-gray-500">
                                    Community aufbauen oder beitreten
                                </div>
                            </button>

                        </div>
                    </>
                )}

                {/* STEP 3 */}
                {step === 3 && (
                    <>
                        <h2 className="text-xl font-semibold text-center mb-4">
                            Du bist startklar 🚀
                        </h2>

                        <p className="text-gray-500 text-center mb-6">
                            Dein Dashboard ist bereit. Du kannst jederzeit erweitern.
                        </p>

                        <button
                            onClick={() => navigate("/dashboard")}
                            className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg"
                        >
                            Zum Dashboard
                        </button>
                    </>
                )}

            </div>
        </div>
    );
}

