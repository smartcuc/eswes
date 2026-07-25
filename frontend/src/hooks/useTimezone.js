/*
# src / hooks / useTimezone.js
*/

import { useSettings } from "./useSettings";

export function useTimezone() {
    const { settings } = useSettings();

    return settings?.timezone || "UTC";
}