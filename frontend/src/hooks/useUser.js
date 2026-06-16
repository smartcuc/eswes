/*
# src/hooks/useUser.js
*/

import { useEffect, useState, useRef } from "react";

export function useUser() {

    // ✅ Cache für instant UI
    const cachedUser = sessionStorage.getItem("user");

    const [user, setUser] = useState(
        cachedUser ? JSON.parse(cachedUser) : null
    );

    const [loading, setLoading] = useState(!cachedUser);
    const [isRefreshing, setIsRefreshing] = useState(false);

    const hasLoadedRef = useRef(false);
    const hasRetriedRef = useRef(false);

    async function loadUser() {

        // ✅ verhindert doppelte calls
        if (hasLoadedRef.current) return;
        hasLoadedRef.current = true;

        setIsRefreshing(true);

        try {

            const res = await fetch("/api/auth/me/", {
                credentials: "include",
            });

            // ✅ nicht eingeloggt
            if (res.status === 401 || res.status === 403) {
                console.warn("No active session");

                setUser(null);
                sessionStorage.removeItem("user");
                return;
            }

            if (!res.ok) {
                throw new Error("User load failed");
            }

            const userData = await res.json();

            const newUser = {
                ...userData,
                memberships: userData.memberships || [],
                is_authenticated: true,
            };

            // ✅ state + cache
            setUser(newUser);
            sessionStorage.setItem("user", JSON.stringify(newUser));

            hasRetriedRef.current = false;

        } catch (err) {

            // ✅ retry nur 1x
            if (!hasRetriedRef.current) {
                console.warn("Retrying user load...", err);

                hasRetriedRef.current = true;
                hasLoadedRef.current = false;

                setTimeout(() => {
                    loadUser();
                }, 200);

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

    // ✅ initial load
    useEffect(() => {
        loadUser();
    }, []);

    // ✅ alle 30s refresh (leichtgewichtig jetzt!)
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
        setUser,
        refreshUser: () => {
            hasLoadedRef.current = false;
            hasRetriedRef.current = false;
            loadUser();
        }
    };
}