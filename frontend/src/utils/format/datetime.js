/*
# src/utils/format/datetime.js
*/

export function formatDateTime(
    value,
    timezone = "UTC",
    locale = "de-DE"
) {
    if (!value) return "";

    return new Intl.DateTimeFormat(
        locale,
        {
            dateStyle: "short",
            timeStyle: "short",
            timeZone: timezone,
        }
    ).format(new Date(value));
}

export function formatHour(
    value,
    timezone = "UTC",
    locale = "de-DE"
) {
    if (!value) return "";

    return new Intl.DateTimeFormat(
        locale,
        {
            hour: "2-digit",
            minute: "2-digit",
            timeZone: timezone,
        }
    ).format(new Date(value));
}
