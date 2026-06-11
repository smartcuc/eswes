/*
# src/hooks/useUser.js
*/

import { useEffect, useState } from "react";

export function setAuthToken(token) {
    localStorage.setItem("access", token);
}

export function useUser() {
    const [user, setUser] = useState({
        onboarding_step: "welcome",
        usage_mode: "standalone",
        memberships: [],
        is_authenticated: false,
    });

    const [loading, setLoading] = useState(true);

    function loadUser() {
        const token = localStorage.getItem("access");

        // ✅ kein Token → sofort sauberer Zustand
        if (!token) {
            setUser({
                onboarding_step: "welcome",
                usage_mode: "standalone",
                memberships: [],
                is_authenticated: false,
            });
            setLoading(false);
            return;
        }

        Promise.all([
            fetch("/api/settings/", {
                headers: { Authorization: `Bearer ${token}` },
            }).then(res => {
                if (!res.ok) throw new Error("Settings failed");
                return res.json();
            }),

            fetch("/api/auth/me/", {
                headers: { Authorization: `Bearer ${token}` },
            }).then(res => {
                if (!res.ok) throw new Error("Me failed");
                return res.json();
            }),
        ])
            .then(([settings, userData]) => {
                setUser({
                    ...userData,

                    onboarding_step: settings.onboarding_step,
                    usage_mode: settings.usage_mode,

                    // ✅ 💥 wichtig: neues Backend-Feld
                    memberships: userData.memberships || [],

                    is_authenticated: true,
                });
            })
            .catch((err) => {
                console.error("User load error:", err);

                // ✅ Token invalid → sauber reset
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");

                setUser({
                    onboarding_step: "welcome",
                    usage_mode: "standalone",
                    memberships: [],
                    is_authenticated: false,
                });
            })
            .finally(() => {
                // ✅ verhindert Flicker
                setLoading(false);
            });
    }

    useEffect(() => {
        loadUser();
    }, []);

    // ✅ RETURN STRUCTURE (wichtig!)
    return { user, loading };
}

