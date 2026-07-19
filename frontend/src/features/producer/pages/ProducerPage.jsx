/*
# src/features/producer/pages/ProducerPage.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export default function ProducerPage() {

    const { data = [] } = useQuery({
        queryKey: ["producers"],
        queryFn: () =>
            apiFetch("/api/producer/"),
    });

    return (
        <div className="p-6">

            <div className="flex items-center justify-between mb-6">

                <div>
                    <h1 className="text-2xl font-semibold">
                        ☀️ Erzeuger
                    </h1>

                    <p className="text-sm text-gray-500 mt-1">
                        Verwalte Photovoltaik, Brennstoffzellen,
                        BHKW und weitere Erzeugersysteme.
                    </p>
                </div>

                <button
                    className="
                        px-4
                        py-2
                        rounded-lg
                        bg-amber-500
                        text-white
                        font-medium
                        shadow-sm
                        hover:bg-amber-600
                        transition-colors
                    "
                >
                    + Erzeuger
                </button>

            </div>

            {data.length === 0 && (

                <div
                    className="
                        bg-white
                        border
                        rounded-xl
                        p-6
                        text-center
                        text-gray-500
                    "
                >
                    Noch keine Erzeugersysteme vorhanden.
                </div>

            )}

            <div className="space-y-4">

                {data.map((producer) => (

                    <div
                        key={producer.id}
                        className="
                            bg-white
                            rounded-xl
                            border
                            border-gray-200
                            shadow-sm
                            p-5
                        "
                    >

                        <div className="flex items-start justify-between">

                            <div>

                                <div className="text-lg font-semibold">
                                    {producer.name}
                                </div>

                                <div className="text-sm text-gray-500 capitalize">
                                    {producer.type}
                                </div>

                            </div>

                        </div>

                        <div
                            className="
                                mt-5
                                grid
                                grid-cols-4
                                gap-4
                            "
                        >

                            <div>
                                <div className="text-xs text-gray-500">
                                    Leistung
                                </div>

                                <div className="font-semibold">
                                    {producer.peak_power_kw} kWp
                                </div>
                            </div>

                            <div>
                                <div className="text-xs text-gray-500">
                                    Strings
                                </div>

                                <div className="font-semibold">
                                    {producer.string_count}
                                </div>
                            </div>

                            <div>
                                <div className="text-xs text-gray-500">
                                    Wechselrichter
                                </div>

                                <div className="font-semibold">
                                    {producer.inverter_power_kw ?? "-"} kW
                                </div>
                            </div>

                            <div>
                                <div className="text-xs text-gray-500">
                                    Speicher
                                </div>

                                <div className="font-semibold">
                                    {producer.battery_capacity_kwh ?? "-"} kWh
                                </div>
                            </div>

                        </div>

                        <div className="mt-4 pt-4 border-t">

                            <div className="text-sm text-gray-500">
                                String-Gesamtleistung
                            </div>

                            <div className="font-semibold text-amber-600">
                                {producer.total_string_power_kwp} kWp
                            </div>
                            <div className="mt-4">

                                <div className="text-sm font-medium text-gray-700 mb-2">
                                    Strings
                                </div>

                                <div className="space-y-2">

                                    {producer.strings?.map((string) => (

                                        <div
                                            key={string.id}
                                            className="
                    flex
                    items-center
                    justify-between
                    rounded-lg
                    bg-slate-50
                    p-3
                "
                                        >

                                            <div>

                                                <div className="font-medium">
                                                    {string.name}
                                                </div>

                                                <div className="text-xs text-gray-500">
                                                    {string.orientation}
                                                    {" • "}
                                                    {string.tilt_deg}°
                                                    {" • "}
                                                    {string.module_count} Module
                                                </div>

                                            </div>

                                            <div
                                                className="
                        text-sm
                        font-semibold
                        text-amber-600
                    "
                                            >
                                                {string.peak_power_kwp} kWp
                                            </div>

                                        </div>

                                    ))}

                                </div>

                            </div>
                        </div>

                    </div>

                ))}

            </div>

        </div>
    );
}
