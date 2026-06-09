/*
# src/hooks/useUser.js
*/

import { useEffect, useState } from "react";

export function useUser() {
    const [user, setUser] = useState(null);

    function loadUser() {
        const token = localStorage.getItem("access");

        if (!token) {
            setUser({
                onboarding_step: "welcome",
                usage_mode: "standalone",
                memberships: [],
                is_authenticated: false,
            });
            return;
        }

        Promise.all([
            fetch("/api/settings/", {
                headers: { Authorization: `Bearer ${token}` },
            }).then(res => res.json()),

            fetch("/api/auth/me/", {
                headers: { Authorization: `Bearer ${token}` },
            }).then(res => res.json()),
        ])
            .then(([settings, userData]) => {
                setUser({
                    ...userData,
                    onboarding_step: settings.onboarding_step,
                    usage_mode: settings.usage_mode,
                    memberships: userData.tenants || [],
                    is_authenticated: true,
                });
            })
            .catch(() => {
                localStorage.removeItem("access");
                localStorage.removeItem("refresh");

                setUser({
                    onboarding_step: "welcome",
                    usage_mode: "standalone",
                    memberships: [],
                    is_authenticated: false,
                });
            });
    }

    useEffect(() => {
        loadUser();
    }, []); // ✅ passt

    // optional:
    useEffect(() => {
        loadUser();
    }, []); // bleibt gleich, aber bewusst


    return user;
}
