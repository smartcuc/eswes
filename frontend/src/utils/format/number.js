/*
# src/utils/format/number.js
*/


export function formatNumber(
    value,
    digits = 2,
    locale = "de-DE"
) {
    return Number(value || 0).toLocaleString(
        locale,
        {
            minimumFractionDigits: digits,
            maximumFractionDigits: digits,
        }
    );
}