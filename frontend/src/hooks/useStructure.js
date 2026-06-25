/*
# src/hooks/useStructure.js
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

export function useHomes() {
    return useQuery({
        queryKey: ["homes"],
        queryFn: () => apiFetch("/api/homes/"),
    });
}

export function useFloors() {
    return useQuery({
        queryKey: ["floors"],
        queryFn: () => apiFetch("/api/floors/"),
    });
}

export function useRooms() {
    return useQuery({
        queryKey: ["rooms"],
        queryFn: () => apiFetch("/api/rooms/"),
    });
}
