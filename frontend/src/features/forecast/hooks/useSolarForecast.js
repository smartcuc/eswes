/*
# src/features/forecast/hooks/useSolarForecast.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export function useSolarForecast(stringId) {
    return useQuery({
        queryKey: ["solar-forecast", stringId],
        enabled: !!stringId,
        queryFn: () =>
            apiFetch(
                `/api/forecast/string/${stringId}/`
            ),
    });
}
