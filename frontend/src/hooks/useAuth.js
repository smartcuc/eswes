/*
# src/hooks/useAuth.js
*/

import { useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";
import { useNavigate } from "react-router-dom";

export function useAuth() {
    const queryClient = useQueryClient();
    const navigate = useNavigate();

    async function logout() {
        try {
            await apiFetch("/api/auth/logout/", {
                method: "POST",
            });
        } catch (err) {
            console.warn("Logout request failed, continue anyway");
        }

        // ✅ ALLES aus dem Cache löschen
        queryClient.clear();

        // ✅ zurück zur Login-Seite
        navigate("/login", { replace: true });
    }

    return { logout };
}
