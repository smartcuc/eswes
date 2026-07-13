/*
# src/components/dashboard/TimezoneAlertBanner.jsx
*/

import { useMemo } from "react";

export default function TimezoneAlertBanner({
    timezone,
    onAccept,
    onSettings,
}) {

    const detectedTimezone = useMemo(
        () =>
            Intl.DateTimeFormat()
                .resolvedOptions()
                .timeZone,
        []
    );

    if (timezone) {
        return null;
    }

    return (
        <div
            className="
                mb-4
                p-4
                rounded-lg
                border
                border-amber-300
                bg-amber-50
                flex
                items-center
                justify-between
            "
        >
            <div>
                <div className="text-amber-900 font-medium">
                    ⚠️ Zeitzone nicht konfiguriert
                </div>

                <div className="text-sm text-amber-800 mt-1">
                    Für korrekte Zeitreihen, Berichte und
                    Benachrichtigungen sollte eine
                    Zeitzone ausgewählt werden.
                </div>

                <div className="text-xs text-amber-700 mt-2">
                    Erkannte Zeitzone:
                    <span className="font-semibold ml-1">
                        {detectedTimezone}
                    </span>
                </div>
            </div>

            <div className="flex gap-2">

                <button
                    onClick={() => onAccept(detectedTimezone)}
                    className="
                        px-3
                        py-1
                        rounded
                        bg-amber-500
                        text-white
                        text-sm
                        hover:bg-amber-600
                    "
                >
                    {detectedTimezone} übernehmen
                </button>

                <button
                    onClick={onSettings}
                    className="
                        px-3
                        py-1
                        rounded
                        border
                        border-amber-300
                        bg-white
                        text-amber-900
                        text-sm
                        hover:bg-amber-100
                    "
                >
                    Einstellungen öffnen
                </button>

            </div>
        </div>
    );
}

