/*
# src/hooks/useSettings.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";


async function fetchSettings() {
    try {
        return await apiFetch("/api/settings/");
    } catch (err) {
        // ✅ nicht eingeloggt / Session fehlt
        if (err?.type === "auth") {
            return null;
        }

        // ✅ andere Fehler weitergeben
        throw err;
    }
}

export function useSettings() {
    const query = useQuery({
        queryKey: ["settings"],
        queryFn: fetchSettings,
        retry: 2,
        staleTime: 1000 * 60 * 5,
    });

    return {
        settings: query.data,
        loading: query.isLoading,
    };
}