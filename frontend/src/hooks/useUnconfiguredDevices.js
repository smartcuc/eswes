/*
# src/hooks/useUnconfiguredDevices.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";


export function useUnconfiguredDevices() {

    return useQuery({
        queryKey: ["devices-unconfigured"],

        queryFn: async () => {
            return await apiFetch("/api/devices/unconfigured/");
        },

        select: (res) => ({
            count: res.devices.length,
            devices: res.devices,
        }),
    });
}
