/*
# src/features/producer/api.js
*/

import { apiFetch } from "../../api/client";

export function getGenerators() {
    return apiFetch("/api/producer/");
}