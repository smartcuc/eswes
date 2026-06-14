/*
# src/hooks/useUser.js
*/

import { useEffect, useState, useRef } from "react";

export function useUser() {

    // ✅ Cache beim Start nutzen (Instant UI!)
    const cachedUser = sessionStorage.getItem("user");

    const [user, setUser] = useState(
        cachedUser ? JSON.parse(cachedUser) : null
    );

    const [loading, setLoading] = useState(!cachedUser);

    // ✅ OPTIONAL 4: Sync Status
    const [isRefreshing, setIsRefreshing] = useState(false);

    const hasLoadedRef = useRef(false);
    const hasRetriedRef = useRef(false);

    async function loadUser() {

        if (hasLoadedRef.current) return;
        hasLoadedRef.current = true;

        setIsRefreshing(true);

        try {

            const [settingsRes, userRes] = await Promise.all([
                fetch("/api/settings/", { credentials: "include" }),
                fetch("/api/auth/me/", { credentials: "include" }),
            ]);

            // ✅ NICHT eingeloggt
            if (userRes.status === 401 || userRes.status === 403) {
                console.warn("No active session");

                setUser(null);
                sessionStorage.removeItem("user");
                return;
            }

            if (!settingsRes.ok || !userRes.ok) {
                throw new Error("User load failed");
            }

            const settings = await settingsRes.json();
            const userData = await userRes.json();

            const newUser = {
                ...userData,
                onboarding_step: settings.onboarding_step,
                usage_mode: settings.usage_mode,
                memberships: userData.memberships || [],
                is_authenticated: true,
            };

            // ✅ Cache + State setzen
            setUser(newUser);
            sessionStorage.setItem("user", JSON.stringify(newUser));

            hasRetriedRef.current = false;

            // ✅ 🔥 Background Sync (nach kurzer Zeit)
            setTimeout(() => {
                fetch("/api/settings/", { credentials: "include" })
                    .then(res => res.ok ? res.json() : null)
                    .then(settings => {
                        if (!settings) return;

                        setUser(prev => {
                            if (!prev) return prev;

                            const updated = {
                                ...prev,
                                onboarding_step: settings.onboarding_step,
                                usage_mode: settings.usage_mode,
                            };

                            sessionStorage.setItem("user", JSON.stringify(updated));
                            return updated;
                        });
                    })
                    .catch(() => { });
            }, 2000);

        } catch (err) {

            if (!hasRetriedRef.current) {
                console.warn("Retrying user load...", err);

                hasRetriedRef.current = true;
                hasLoadedRef.current = false;

                setTimeout(() => {
                    loadUser();
                }, 150);

                return;
            }

            console.error("User load failed permanently:", err);

            setUser(null);
            sessionStorage.removeItem("user");

        } finally {
            setLoading(false);
            setIsRefreshing(false);
        }
    }

    // ✅ Initial Load
    useEffect(() => {
        loadUser();
    }, []);

    // ✅ 🔥 Auto Sync alle 30s
    useEffect(() => {

        const interval = setInterval(() => {
            hasLoadedRef.current = false;
            loadUser();
        }, 30000);

        return () => clearInterval(interval);

    }, []);

    return {
        user,
        loading,
        isRefreshing,

        refreshUser: () => {
            hasLoadedRef.current = false;
            hasRetriedRef.current = false;
            loadUser();
        }
    };
}
