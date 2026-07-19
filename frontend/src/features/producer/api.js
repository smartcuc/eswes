/*
# src/features/producer/api.js
*/

import { apiFetch } from "../../api/client";

export function getGenerators() {
    return apiFetch("/api/producer/");
}

export function getGeneratorTypes() {
    return apiFetch("/api/producer/types/");
}

export function getOrientations() {
    return apiFetch("/api/producer/orientations/");
}
