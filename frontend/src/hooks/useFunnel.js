import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "../api/client"

export function useFunnel() {
    return useQuery({
        queryKey: ["funnel"],
        queryFn: () => apiFetch("/funnel/"),
    })
}