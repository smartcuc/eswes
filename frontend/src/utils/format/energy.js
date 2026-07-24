/*
# src/utils/format/energy.js
*/

import { formatNumber } from "./number";

export function formatEnergy(
    value,
    digits = 2
) {
    return `${formatNumber(value, digits)} kWh`;
}

export function formatPower(
    value,
    digits = 2
) {
    return `${formatNumber(value, digits)} W`;
}