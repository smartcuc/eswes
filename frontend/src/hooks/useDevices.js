/*
# src/hooks/useDevices.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useDevices() {
    return useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
        staleTime: 5000,
    });
}

// ✅ NEU – für Dashboard

// ✅ Device Status (Dashboard RAW)
export function useDeviceStatus() {
    return useQuery({
        queryKey: ["device-status"],
        queryFn: () => apiFetch("/api/devices/status/"),
        staleTime: 5000,
    });
}


// ✅ OPTIONAL: Aggregation für Dashboard
export function useDeviceSummary() {
    return useQuery({
        queryKey: ["device-status"],
        queryFn: async () => {
            const devices = await apiFetch("/api/devices/status/");

            return {
                total: devices.length,
                online: devices.filter(d => d.status === "online").length,
                offline: devices.filter(d => d.status === "offline").length,
                stale: devices.filter(d => d.status === "stale").length,
            };
        },
        staleTime: 5000,
    });
}

