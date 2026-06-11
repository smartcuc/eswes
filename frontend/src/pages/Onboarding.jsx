/*
# src/pages/Onboarding.jsx
*/

import { useEffect, useState } from "react";
import { apiFetch } from "../api";
import { texts } from "../i18n";
import { useLang } from "../hooks/useLang";


// ✅ Helper
function updateStep(nextStep, setStep) {
    apiFetch("/api/onboarding-step/", {
        method: "POST",
        body: JSON.stringify({ step: nextStep }),
    })
        .then(res => {
            if (!res.ok) throw new Error();
            return res.json();
        })
        .then(() => {
            setStep(nextStep);
        })
        .catch(() => {
            console.error("Error updating step");
        });
}


// ✅ MAIN COMPONENT
export default function Onboarding() {
    const [step, setStep] = useState("welcome");

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const invite = params.get("token") || params.get("invite");

        if (invite) {
            apiFetch("/api/use-invite/", {
                method: "POST",
                body: JSON.stringify({ token: invite }),
            })
                .then(() => {
                    updateStep("energy", setStep);
                })
                .catch(() => {
                    console.error("Invite failed");
                });
        } else {
            apiFetch("/api/settings/")
                .then(res => res.json())
                .then(data => {
                    const s = data.onboarding_step || "welcome";
                    console.log("ONBOARDING STEP:", s);
                    setStep(s);
                })
                .catch(() => {
                    setStep("welcome");
                });
        }
    }, []);

    // ✅ 🔥 FIX: DONE redirect
    useEffect(() => {
        if (step === "done") {
            window.location.href = "/"; // Dashboard
        }
    }, [step]);

    const steps = ["welcome", "profile", "meter", "energy", "billing", "done"];
    const progress = ((steps.indexOf(step) + 1) / steps.length) * 100;

    return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
            <div className="w-full max-w-md bg-white shadow-lg rounded-2xl p-6">

                {/* Progress */}
                <div className="w-full bg-gray-200 h-2 rounded mb-6">
                    <div
                        className="bg-indigo-600 h-2 rounded transition"
                        style={{ width: `${progress}%` }}
                    />
                </div>

                {/* Steps */}
                {step === "welcome" && <Welcome setStep={setStep} />}
                {step === "profile" && <Profile setStep={setStep} />}
                {step === "meter" && <Meter setStep={setStep} />}
                {step === "energy" && <Energy setStep={setStep} />}
                {step === "billing" && <Billing setStep={setStep} />}

                {/* ✅ FALLBACK FIX */}
                {!step && <Welcome setStep={setStep} />}

            </div>
        </div>
    );
}

// ✅ Welcome
function Welcome({ setStep }) {
    return (
        <div className="text-center">
            <h1 className="text-2xl font-bold mb-2">Willkommen 👋</h1>
            <p className="text-gray-600 mb-6">
                Wir richten dein System in wenigen Schritten ein.
            </p>

            <button
                onClick={() => updateStep("profile", setStep)}
                className="w-full bg-indigo-600 text-white py-3 rounded-xl"
            >
                Start
            </button>
        </div>
    );
}


// ✅ Profile
function Profile({ setStep }) {
    const [form, setForm] = useState({
        first_name: "",
        last_name: "",
        street: "",
        city: "",
    });

    function handleChange(e) {
        setForm({ ...form, [e.target.name]: e.target.value });
    }

    function submit() {
        apiFetch("/api/profile/", {
            method: "POST",
            body: JSON.stringify(form),
        })
            .then(res => {
                if (!res.ok) throw new Error();
                updateStep("meter", setStep);
            })
            .catch(() => {
                alert("Profil speichern fehlgeschlagen");
            });
    }

    return (
        <div>
            <h2 className="text-xl mb-4">Dein Profil</h2>

            <div className="space-y-3">
                <input name="first_name" placeholder="Vorname" onChange={handleChange} className="w-full border p-3 rounded-lg" />
                <input name="last_name" placeholder="Nachname" onChange={handleChange} className="w-full border p-3 rounded-lg" />
                <input name="street" placeholder="Straße" onChange={handleChange} className="w-full border p-3 rounded-lg" />
                <input name="city" placeholder="Stadt" onChange={handleChange} className="w-full border p-3 rounded-lg" />
            </div>

            <button
                onClick={submit}
                className="w-full mt-6 bg-indigo-600 text-white py-3 rounded-xl"
            >
                Weiter
            </button>
        </div>
    );
}


// ✅ Meter
function Meter({ setStep }) {
    const { lang } = useLang();
    const t = texts[lang];

    const [selected, setSelected] = useState(null);
    const [loading, setLoading] = useState(false);

    function selectMode(mode) {
        if (loading) return;

        setLoading(true);
        setSelected(mode);

        apiFetch("/api/usage-mode/", {
            method: "POST",
            body: JSON.stringify({ usage_mode: mode }),
        })
            .then(res => {
                if (!res.ok) throw new Error();

                setTimeout(() => {
                    updateStep("energy", setStep);
                }, 250);
            })
            .catch(() => {
                alert("Fehler beim Speichern");
                setLoading(false);
            });
    }

    return (
        <div>
            <h2 className="text-xl mb-4">{t.usage_question}</h2>

            <div className="space-y-3">

                {/* Standalone */}
                <button
                    disabled={loading}
                    onClick={() => selectMode("standalone")}
                    className={`w-full border p-4 rounded-xl text-left transition
            ${selected === "standalone" ? "border-indigo-600 bg-indigo-50" : ""}
            ${loading ? "opacity-50 cursor-not-allowed" : ""}
          `}
                >
                    <div className="font-medium">{t.standalone}</div>
                    <div className="text-sm text-gray-500">
                        {t.standalone_desc}
                    </div>
                </button>

                {/* Tenant */}
                <button
                    disabled={loading}
                    onClick={() => selectMode("tenant")}
                    className={`w-full border p-4 rounded-xl text-left transition
            ${selected === "tenant" ? "border-indigo-600 bg-indigo-50" : ""}
            ${loading ? "opacity-50 cursor-not-allowed" : ""}
          `}
                >
                    <div className="font-medium">Community</div>
                    <div className="text-sm text-gray-500">
                        Du bist Teil einer Energie-Community
                    </div>
                </button>

            </div>
        </div>
    );
}


// ✅ Energy
function Energy({ setStep }) {
    return (
        <div>
            <h2 className="text-xl mb-4">Energie verbinden ⚡</h2>

            <button
                onClick={() => updateStep("billing", setStep)}
                className="w-full bg-indigo-600 text-white py-3 rounded-xl"
            >
                Weiter
            </button>
        </div>
    );
}


// ✅ Billing
function Billing({ setStep }) {
    return (
        <div>
            <h2 className="text-xl mb-4">Abrechnung</h2>

            <button
                onClick={() => updateStep("done", setStep)}
                className="w-full bg-indigo-600 text-white py-3 rounded-xl"
            >
                Fertig
            </button>
        </div>
    );
}
