/*
# src/hooks/useDeviceMeta.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";


export function useDeviceRoles() {
    return useQuery({
        queryKey: ["device_roles"],
        queryFn: () => apiFetch("/api/device-roles/"),
    });
}

export function useGeneratorTypes() {
    return useQuery({
        queryKey: ["generator_types"],
        queryFn: () => apiFetch("/api/producer/types/"),
    });
}