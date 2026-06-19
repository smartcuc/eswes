/*
# src/hooks/useUser.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";


async function fetchUser() {
    try {
        const userData = await apiFetch("/api/auth/me/");

        return {
            ...userData,
            memberships: userData.memberships || [],
            is_authenticated: true,
        };

    } catch (err) {
        // ✅ Auth verloren → null
        if (err?.type === "auth") {
            return null;
        }

        throw err;
    }
}


export function useUser() {
    const query = useQuery({
        queryKey: ["user"],
        queryFn: fetchUser,

        // ✅ wichtig für dein Setup
        retry: 1,
        staleTime: 1000 * 60 * 5,   // 5 Minuten Cache
        refetchOnWindowFocus: false,
    });

    return {
        user: query.data ?? null,
        loading: query.isLoading,
        isRefreshing: query.isFetching,

        // ✅ Ersatz für dein refreshUser
        refreshUser: query.refetch,
    };
}
