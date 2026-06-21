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
