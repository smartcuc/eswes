/*
# src/hooks/useUnconfiguredDevices.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useUnconfiguredDevices() {

    return useQuery({
        queryKey: ["devices"],
        queryFn: async () => {
            const res = await apiFetch("/api/devices/");
            return res;
        },
        select: (devices) => {
            const unconfigured = devices.filter(
                (d) => !d.type || !d.role
            );

            return {
                count: unconfigured.length,
                devices: unconfigured,
            };
        },
    });
}
