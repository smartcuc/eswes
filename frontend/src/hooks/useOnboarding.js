/*
# src/hooks/useOnboarding.js
*/

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useOnboarding() {
    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (step) =>
            apiFetch("/api/onboarding-step/", {
                method: "POST",
                body: JSON.stringify({ onboarding_step: step }),
            }),

        onSuccess: (_, step) => {
            // ✅ sofort cache updaten
            queryClient.setQueryData(["settings"], (old) => ({
                ...old,
                onboarding_step: step,
            }));
        },
    });
}