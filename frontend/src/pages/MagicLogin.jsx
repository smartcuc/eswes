/*
# src/pages/MagicLogin.jsx
*/

import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function MagicLogin() {

    const navigate = useNavigate();

    useEffect(() => {

        const params = new URLSearchParams(window.location.search);
        const token = params.get("token");

        async function login() {
            if (!token) {
                navigate("/login");
                return;
            }

            try {
                const res = await fetch(`/api/magic-login/?token=${token}`, {
                    credentials: "include",
                });

                if (!res.ok) {
                    throw new Error("Login failed");
                }

                // ✅ Session sicherstellen
                let meRes = await fetch("/api/auth/me/", {
                    credentials: "include",
                });

                if (!meRes.ok) {
                    await new Promise(r => setTimeout(r, 100));

                    meRes = await fetch("/api/auth/me/", {
                        credentials: "include",
                    });

                    if (!meRes.ok) {
                        throw new Error("Session not ready");
                    }
                }

                // ✅ Settings laden
                const settingsRes = await fetch("/api/settings/", {
                    credentials: "include",
                });

                if (!settingsRes.ok) {
                    throw new Error("Settings failed");
                }

                // ✅ Daten kombinieren
                const settings = await settingsRes.json();
                const userData = await meRes.json();

                const newUser = {
                    ...userData,
                    onboarding_step: settings.onboarding_step,
                    usage_mode: settings.usage_mode,
                    memberships: userData.memberships || [],
                    is_authenticated: true,
                };

                // ✅ 🔥 PRE-CACHE
                sessionStorage.setItem("user", JSON.stringify(newUser));

                // ✅ URL bereinigen
                window.history.replaceState({}, "", "/");

                navigate("/app");

            } catch (err) {
                console.error(err);
                navigate("/login");
            }
        }

        login();

    }, [navigate]);

    return (
        <div className="p-6 text-center">
            <h2 className="text-xl">Logging you in...</h2>
        </div>
    );
}
