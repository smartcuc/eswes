/*
# src/pages/Login.jsx
*/
import { useState } from "react";

export default function Login() {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("");
    const [cooldown, setCooldown] = useState(0);

    async function handleLogin() {
        if (!email || loading || cooldown > 0) return;

        setLoading(true);
        setStatus("");

        try {
            const res = await fetch("/api/request-magic-link/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ email }),
            });

            const data = await res.json();

            if (!res.ok) {
                throw new Error(data.error || "Fehler");
            }

            setStatus("✅ Check deine E-Mails – dein Login-Link ist unterwegs!");
            setEmail("");

            // ✅ cooldown starten (15 Sekunden)
            let seconds = 15;
            setCooldown(seconds);

            const interval = setInterval(() => {
                seconds--;
                setCooldown(seconds);

                if (seconds <= 0) {
                    clearInterval(interval);
                }
            }, 1000);

        } catch (err) {
            setStatus("❌ Fehler beim Senden. Bitte erneut versuchen.");
        }

        setLoading(false);
    }

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 p-6">

            <div className="bg-white w-full max-w-md rounded-2xl shadow-xl p-8">

                {/* HEADER */}
                <div className="text-center mb-6">
                    <h1 className="text-2xl font-bold">
                        Sharegy ⚡
                    </h1>
                    <p className="text-sm text-gray-500">
                        Energie verstehen & intelligent nutzen
                    </p>
                </div>

                {/* TITLE */}
                <h2 className="text-xl font-semibold text-center mb-2">
                    Willkommen zurück 👋
                </h2>

                <p className="text-gray-500 text-sm text-center mb-6">
                    Gib deine E-Mail ein – wir schicken dir einen sicheren Login-Link.
                </p>

                {/* INPUT */}
                <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="deine@email.de"
                    autoFocus
                    onKeyDown={(e) => {
                        if (e.key === "Enter") handleLogin();
                    }}
                    className="w-full border border-gray-300 p-3 rounded-lg mb-4 focus:outline-none focus:ring-2 focus:ring-indigo-500"
                />

                {/* BUTTON */}
                <button
                    onClick={handleLogin}
                    disabled={loading || cooldown > 0}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 text-white py-3 rounded-lg font-medium transition transform hover:scale-[1.02] disabled:opacity-50"
                >
                    {loading
                        ? "Sende Login-Link…"
                        : cooldown > 0
                            ? `Erneut senden in ${cooldown}s`
                            : "Login-Link erhalten"}
                </button>

                {/* STATUS */}
                {status && (
                    <p className="mt-4 text-sm text-center text-gray-600">
                        {status}
                    </p>
                )}

                {/* SPAM HINWEIS ✅ */}
                {status && (
                    <p className="mt-2 text-xs text-center text-gray-400">
                        Falls du nichts siehst: prüfe bitte auch deinen Spam-Ordner 📬
                    </p>
                )}

                {/* FOOTER */}
                <div className="mt-6 text-xs text-gray-400 text-center">
                    🔒 Kein Passwort nötig – sicher per Magic Link
                </div>

                <div className="mt-6 text-sm text-center">
                    <a href="/" className="text-indigo-500 hover:underline">
                        ← Zurück zur Startseite
                    </a>
                </div>

            </div>
        </div>
    );
}
