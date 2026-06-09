/*
# src/pages/Join.jsx
*/

import { useEffect, useState } from "react";
import { apiFetch } from "../api";

export default function Join() {
    const [token, setToken] = useState("");
    const [status, setStatus] = useState("");
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const t = params.get("token");

        if (t) {
            setToken(t);
            handleJoin(); // 🔥 auto-join
        }
    }, []);


    async function handleJoin() {
        if (!token) return;

        setLoading(true);

        const res = await apiFetch("/api/use-invite/", {
            method: "POST",
            body: JSON.stringify({ token }),
        });

        const data = await res.json();

        if (res.ok) {
            setStatus("✅ Erfolgreich beigetreten");

            setTimeout(() => {
                window.location.reload();
            }, 800);
        } else {
            setStatus(data.error || "❌ Ungültiger Invite");
            setLoading(false);
        }
    }

    return (
        <div className="max-w-md mx-auto p-6">

            <h1 className="text-2xl font-bold mb-4">
                Community beitreten
            </h1>

            <p className="text-sm text-gray-500 mb-4">
                Gib deinen Invite-Code ein oder nutze einen Link.
            </p>

            <input
                value={token}
                onChange={(e) => setToken(e.target.value)}
                placeholder="Invite Code"
                className="border p-3 w-full mb-4 rounded"
            />

            <button
                onClick={handleJoin}
                disabled={loading}
                className="bg-indigo-600 text-white w-full py-3 rounded"
            >
                {loading ? "Beitreten..." : "Beitreten"}
            </button>

            {status && (
                <p className="mt-4 text-sm">
                    {status}
                </p>
            )}

        </div>
    );
}

