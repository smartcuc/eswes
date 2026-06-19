/*
# src/pages/Onboarding.jsx
*/

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useSettings } from "../hooks/useSettings";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export default function Onboarding() {
    const navigate = useNavigate();
    const queryClient = useQueryClient();

    const { settings } = useSettings();

    const mutation = useMutation({
        mutationFn: async (step) => {
            await apiFetch("/api/onboarding-step/", {
                method: "POST",
                body: JSON.stringify({
                    onboarding_step: step,
                }),
            });
        },

        onSuccess: (_, step) => {
            queryClient.setQueryData(["settings"], (old) => {
                if (!old) return old;
                return {
                    ...old,
                    onboarding_step: step,
                };
            });
        },
    });

    useEffect(() => {
        if (!settings) return;

        if (settings.onboarding_step === "done") {
            navigate("/app/dashboard", { replace: true });
        }
    }, [settings, navigate]);

    const started = settings && settings.onboarding_step === "setup";

    function updateStep(step) {
        if (mutation.isLoading) return;

        mutation.mutate(step, {
            onSuccess: () => {
                if (step === "done") {
                    navigate("/app/dashboard", { replace: true });
                }
            },
        });
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 flex items-center justify-center p-6">
            <div className="bg-white w-full max-w-xl rounded-2xl shadow-xl p-8">

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
                            disabled={mutation.isLoading}
                            className="mt-8 w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg transition"
                        >
                            {mutation.isLoading ? "…" : "Los geht’s"}
                        </button>
                    </>
                )}

                {started && (
                    <>
                        <h2 className="text-xl font-semibold text-center mb-4">
                            Dein Dashboard ist bereit 🚀
                        </h2>

                        <p className="text-gray-500 text-center mb-6">
                            Starte jetzt mit deinem Energiemanagement.
                        </p>

                        <button
                            onClick={() => updateStep("done")}
                            disabled={mutation.isLoading}
                            className="w-full bg-orange-500 hover:bg-orange-600 text-white py-3 rounded-lg"
                        >
                            {mutation.isLoading ? "…" : "Zum Dashboard"}
                        </button>
                    </>
                )}

            </div>
        </div>
    );
}