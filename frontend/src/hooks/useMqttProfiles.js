/*
# src/hooks/useMqttProfiles.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useMqttProfiles() {
    return useQuery({
        queryKey: ["mqtt-profiles"],
        queryFn: () =>
            apiFetch("/api/devices/mqtt-profiles/"),
    });
}
