/*
# src/pages/Login.jsx
*/

import { useState } from "react";

export default function Login() {
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [status, setStatus] = useState("");

    async function handleLogin() {
        if (!email) return;

        setLoading(true);

        const res = await fetch("/api/request-magic-link/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email }),
        });

        const data = await res.json();

        if (!res.ok) {
            setStatus(data.error || "Fehler beim Senden");
            setLoading(false);
            return;
        }

        setStatus("✅ Login-Link gesendet. Bitte prüfe deine E-Mails.");
        setLoading(false);
    }

    return (
        <div className="max-w-md mx-auto p-6">

            <h1 className="text-2xl font-bold mb-2">
                Willkommen 👋
            </h1>

            <p className="text-sm text-gray-500 mb-6">
                Gib deine E-Mail ein.
                <br />
                Wir senden dir einen sicheren Login-Link.
            </p>

            <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="deine@email.de"
                className="border p-3 w-full mb-4 rounded"
            />

            <button
                onClick={handleLogin}
                disabled={loading}
                className="bg-indigo-600 text-white w-full py-3 rounded"
            >
                {loading ? "Sende..." : "Link senden"}
            </button>

            {status && (
                <p className="mt-4 text-sm">{status}</p>
            )}

        </div>
    );
}
