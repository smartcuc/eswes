import { useQuery } from "@tanstack/react-query"
import { apiFetch } from "../api/apiFetch"

export function useKpis() {
    return useQuery({
        queryKey: ["kpis"],
        queryFn: () => apiFetch("/kpis/"),
    })
}