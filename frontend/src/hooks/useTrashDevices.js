/*
# src/hooks/useTrashDevices.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useTrashDevices() {

    return useQuery({
        queryKey: ["device-trash"],
        queryFn: () => apiFetch("/api/devices/trash/"),
    });
}

export function useTrashCount() {

    return useQuery({
        queryKey: ["device-trash-count"],
        queryFn: () => apiFetch("/api/devices/trash/count/"),
    });
}
