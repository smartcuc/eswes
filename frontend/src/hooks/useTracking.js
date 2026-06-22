/*
# src/hooks/useTracking.js
*/

import { useQuery } from "@tanstack/react-query";
import apiFetch from "../lib/apiFetch";

export function useTrackingKPIs(days = 7) {
    return useQuery({
        queryKey: ["tracking-kpis", days],
        queryFn: () => apiFetch(`/tracking/kpis?days=${days}`),
    });
}

export function useTrackingFunnel(days = 7) {
    return useQuery({
        queryKey: ["tracking-funnel", days],
        queryFn: () => apiFetch(`/tracking/funnel?days=${days}`),
    });
}
