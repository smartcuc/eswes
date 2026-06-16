/*
# src/pages/Onboarding.jsx
*/

import { useEffect, useState } from "react";

export default function Onboarding({ refreshUser, user }) {
    const [started, setStarted] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    // ✅ Step aus Backend berücksichtigen
    useEffect(() => {
        if (user?.onboarding_step === "setup") {
            setStarted(true);
        }
    }, [user]);

    async function updateStep(nextStep) {
        setLoading(true);
        setError("");

        try {
            const res = await fetch("/api/settings/update/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                credentials: "include", // ✅ CRITICAL
                body: JSON.stringify({
                    onboarding_step: nextStep,
                }),
            });

            if (!res.ok) {
                throw new Error("Update failed");
            }

            if (nextStep === "done") {
                await refreshUser();
            } else {
                setStarted(true);
            }

        } catch (err) {
            console.error("Onboarding error:", err);
            setError("❌ Etwas ist schiefgelaufen. Bitte erneut versuchen.");
        }

        setLoading(false);
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-6">

            <div className="bg-white w-full max-w-xl rounded-2xl shadow-xl p-8">

                {/* STEP 1 */}
                {!started && (
                    <>
                        <h1 className="text-2xl font-bold text-center mb-4">
                            Willkommen bei Sharegy ⚡
                        </h1>

                        <p className="text-gray-500 text-center mb-6">
                            Dein persönliches Energy Dashboard ist nur einen Schritt entfernt.
                        </p>

                        <div className="space-y-3 text-gray-700 text-sm">
                            <p>✅ Echtzeit Energieübersicht</p>
                            <p>✅ Produktion & Verbrauch im Blick</p>
                            <p>✅ Automatische Optimierung</p>
                        </div>

                        <button
                            onClick={() => updateStep("setup")}
                            className="mt-8 w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg transition"
                        >
                            Los geht’s
                        </button>
                    </>
                )}

                {/* STEP 2 */}
                {started && (
                    <>
                        <h2 className="text-xl font-semibold text-center mb-4">
                            Dein Dashboard ist bereit 🚀
                        </h2>

                        <p className="text-gray-500 text-center mb-6">
                            Starte jetzt mit deinem Energiemanagement.
                        </p>

                        <div className="bg-gray-50 p-4 rounded-lg text-sm text-gray-600 mb-6 text-center">
                            💡 Tipp: Du kannst jederzeit später eine Community erstellen
                            oder dich mit anderen Nutzern vernetzen.
                        </div>

                        <button
                            onClick={() => updateStep("done")}
                            disabled={loading}
                            className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg font-medium transition transform hover:scale-[1.02] disabled:opacity-50"
                        >
                            {loading ? "Starte…" : "Zum Dashboard"}
                        </button>

                        {error && (
                            <p className="mt-4 text-sm text-center text-red-500">
                                {error}
                            </p>
                        )}
                    </>
                )}

            </div>

        </div>
    );
}