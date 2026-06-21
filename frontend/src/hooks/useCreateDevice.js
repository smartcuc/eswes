/*
# src/hooks/useCreateDevice.js
*/

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useCreateDevice() {

    const queryClient = useQueryClient();

    return useMutation({
        mutationFn: (data) =>
            apiFetch("/api/devices/", {
                method: "POST",
                body: JSON.stringify(data),
            }),

        onSuccess: () => {
            // ✅ Devices neu laden
            queryClient.invalidateQueries(["devices"]);
        },
    });
}
