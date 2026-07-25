/*
# src/features/forecast/ForecastPage.jsx
*/

import ForecastChart from "./ForecastChart";
import { useSolarForecast } from "./hooks/useSolarForecast";
import { useTimezone } from "../../hooks/useTimezone";
import { formatHour, formatNumber, } from "../../utils/format";


export default function ForecastPage() {

    // 🔥 erst einmal fest verdrahtet
    // TODO:
    // Nach Einführung der String-Auswahl
    // dynamisch aus Route oder Select laden.
    const stringId =
        "75830ffa-8dd0-445c-ace9-078cbec64ffc";

    const timezone = useTimezone();

    const query = useSolarForecast(
        stringId
    );

    const points =
        query.data?.points || [];

    const totalForecast = points.reduce(
        (sum, p) => sum + Number(p.v || 0),
        0
    );

    const peak =
        points.length > 0
            ? points.reduce(
                (a, b) =>
                    b.v > a.v ? b : a
            )
            : null;

    const nextHour =
        points.length > 0
            ? points[0]
            : null;

    return (
        <div className="p-6 space-y-6">

            <div>
                <h1 className="text-2xl font-bold">
                    ☀️ Solar Forecast
                </h1>

                <p className="text-gray-500">
                    Physikalische Prognose · nächste 24 Stunden
                </p>
            </div>

            {query.isLoading && (
                <div className="bg-white rounded-xl shadow p-6">
                    Forecast wird geladen...
                </div>
            )}

            {query.isError && (
                <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-600">
                    Forecast konnte nicht geladen werden.
                </div>
            )}

            {!query.isLoading && !query.isError && (
                <>
                    {!points.length && (
                        <div className="
                bg-yellow-50
                border
                border-yellow-200
                rounded-xl
                p-4
                text-yellow-800
            ">
                            ⚠️ Keine Forecast-Daten verfügbar.
                        </div>
                    )}

                    {points.length > 0 && (
                        <>
                            {/* KPIs */}

                            <div className="grid grid-cols-4 gap-4">

                                <div className="bg-white rounded-xl shadow p-4">
                                    <div className="text-sm text-gray-500">
                                        ☀️ Tagesertrag
                                    </div>

                                    <div className="text-4xl font-bold text-amber-600">
                                        {formatNumber(totalForecast)}
                                    </div>

                                    <div className="text-xs text-gray-500">
                                        kWh
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow p-4">
                                    <div className="text-sm text-gray-500">
                                        📈 Peak
                                    </div>

                                    <div className="text-3xl font-bold text-orange-500">
                                        {peak
                                            ? formatNumber(peak.v)
                                            : formatNumber(0)}
                                    </div>

                                    <div className="text-xs text-gray-500">
                                        kWh
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow p-4">
                                    <div className="text-sm text-gray-500">
                                        🕒 Peak-Zeit
                                    </div>

                                    <div className="text-3xl font-bold text-slate-700">
                                        {peak
                                            ? formatHour(
                                                peak.t * 1000,
                                                timezone
                                            )
                                            : "--:--"}
                                    </div>
                                </div>

                                <div className="bg-white rounded-xl shadow p-4">
                                    <div className="text-sm text-gray-500">
                                        ⚡ Nächste Stunde
                                    </div>

                                    <div className="text-3xl font-bold text-blue-600">
                                        {nextHour
                                            ? formatNumber(nextHour.v)
                                            : formatNumber(0)}
                                    </div>

                                    <div className="text-xs text-gray-500">
                                        kWh
                                    </div>
                                </div>

                            </div>

                            {/* CHART */}

                            <div className="bg-white rounded-xl shadow p-4">

                                <div className="mb-4">
                                    <div className="font-semibold">
                                        Dach-Nord
                                    </div>

                                    <div className="text-sm text-gray-500">
                                        Forecast nächste 24 Stunden
                                    </div>
                                </div>

                                <ForecastChart
                                    points={points}
                                />

                            </div>
                        </>
                    )}
                </>
            )}
        </div>
    )
}
