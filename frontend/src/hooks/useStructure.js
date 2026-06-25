/*
# src/hooks/useStructure.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";


export function useStructure() {
    return useQuery({
        queryKey: ["structure"],
        queryFn: async () => {
            return await apiFetch("/api/devices/setup-options/");
        },
    });
}
