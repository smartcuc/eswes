/*
# src/pages/Profile.jsx
*/

import { useEffect, useState } from "react";
import Card from "../components/ui/Card";
import { apiFetch } from "../api/client";
import { useSettings } from "../hooks/useSettings";
import { useQuery, useQueryClient } from "@tanstack/react-query";

export default function Profile() {

    const queryClient = useQueryClient();

    const { settings } = useSettings();

    const [timezone, setTimezone] = useState("");
    const [language, setLanguage] = useState("de");
    const [saved, setSaved] = useState(false);

    const timezoneQuery = useQuery({
        queryKey: ["timezones"],
        queryFn: () => apiFetch("/api/timezones/"),
        staleTime: Infinity,
    });

    const commonTimezones =
        timezoneQuery.data?.filter((tz) =>
            tz.startsWith("Europe/") ||
            tz === "UTC"
        );

    useEffect(() => {

        if (!settings) {
            return;
        }

        setTimezone(settings.timezone || "");
        setLanguage(settings.language || "de");

    }, [settings]);

    async function saveTimezone() {

        await apiFetch("/api/timezone/", {
            method: "POST",
            body: JSON.stringify({
                timezone,
            }),
        });

        await queryClient.invalidateQueries({
            queryKey: ["settings"],
        });

        setSaved(true);

        setTimeout(() => {
            setSaved(false);
        }, 3000);
    }

    async function saveLanguage() {

        await apiFetch("/api/language/", {
            method: "POST",
            body: JSON.stringify({
                language,
            }),
        });

        await queryClient.invalidateQueries({
            queryKey: ["settings"],
        });

        setSaved(true);

        setTimeout(() => {
            setSaved(false);
        }, 3000);
    }


    return (
        <div className="max-w-5xl mx-auto p-6 space-y-6">

            <div>
                <h1 className="text-3xl font-bold text-gray-900">
                    Profil
                </h1>

                <p className="text-gray-500 mt-1">
                    Persönliche Daten und Präferenzen.
                </p>
            </div>
            {saved && (
                <div
                    className="
                        rounded-lg
                        border
                        border-green-200
                        bg-green-50
                        px-4
                        py-3
                        text-green-700
                    "
                >
                    ✅ Einstellungen wurden gespeichert.
                </div>
            )}
            <div className="grid gap-6 lg:grid-cols-2">

                <Card>

                    <h2 className="text-lg font-semibold mb-4">
                        👤 Benutzer
                    </h2>

                    <div className="text-sm text-gray-500">
                        Weitere Benutzerdaten folgen.
                    </div>

                </Card>

                <Card>

                    <h2 className="text-lg font-semibold mb-4">
                        🌍 Region & Sprache
                    </h2>

                    <div className="space-y-4">

                        <div>

                            <label className="block text-sm font-medium mb-2">
                                Zeitzone
                            </label>

                            <select
                                value={timezone}
                                onChange={(e) => setTimezone(e.target.value)}
                                className="
                                    w-full
                                    border
                                    rounded-lg
                                    px-3
                                    py-2
                                    bg-white
                                "
                            >
                                <option value="">
                                    Bitte auswählen
                                </option>

                                {commonTimezones?.map((tz) => (
                                    <option
                                        key={tz}
                                        value={tz}
                                    >
                                        {tz}
                                    </option>
                                ))}

                            </select>


                        </div>

                        <div>

                            <label className="block text-sm font-medium mb-2">
                                Sprache
                            </label>

                            <select
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="
                                    w-full
                                    border
                                    rounded-lg
                                    px-3
                                    py-2
                                "
                            >
                                <option value="de">
                                    Deutsch
                                </option>

                                <option value="en">
                                    English
                                </option>

                            </select>

                        </div>

                        <div className="flex gap-2">

                            <button
                                onClick={() =>
                                    setTimezone(
                                        Intl.DateTimeFormat()
                                            .resolvedOptions()
                                            .timeZone
                                    )
                                }
                                className="
                                    px-3 py-2
                                    border
                                    rounded-lg
                                "
                            >
                                Automatisch erkennen
                            </button>

                            <button
                                onClick={saveTimezone}
                                className="
                                    px-3 py-2
                                    rounded-lg
                                    bg-indigo-600
                                    text-white
                                "
                            >
                                Zeitzone speichern
                            </button>

                            <button
                                onClick={saveLanguage}
                                className="
                                    px-3 py-2
                                    rounded-lg
                                    bg-indigo-600
                                    text-white
                                "
                            >
                                Sprache speichern
                            </button>

                        </div>

                    </div>

                </Card>

            </div>

        </div>
    );
}

