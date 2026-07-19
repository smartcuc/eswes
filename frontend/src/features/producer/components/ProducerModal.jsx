/*
# src/features/producer/components/ProducerModal.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { getGenerators } from "../api";

export default function ProducerModal({
    open,
    onClose,
}) {

    const { data = [] } = useQuery({
        queryKey: ["generators"],
        queryFn: getGenerators,
        enabled: open,
    });

    if (!open) {
        return null;
    }

    return (
        <div
            className="
                fixed inset-0
                bg-black/40
                flex items-center justify-center
                z-50
            "
            onClick={onClose}
        >
            <div
                className="
                    bg-white
                    rounded-2xl
                    shadow-xl
                    max-w-4xl
                    w-full
                    h-[80vh]
                    overflow-auto
                    p-6
                "
                onClick={(e) => e.stopPropagation()}
            >

                <div
                    className="
                        flex
                        justify-between
                        items-center
                        mb-6
                    "
                >
                    <h2 className="text-xl font-semibold">
                        ☀️ Erzeuger
                    </h2>

                    <button
                        onClick={onClose}
                        className="text-gray-400"
                    >
                        ✕
                    </button>
                </div>

                <div className="space-y-4">

                    {data.map((system) => (

                        <div
                            key={system.id}
                            className="
                                border
                                rounded-xl
                                p-4
                                bg-white
                            "
                        >

                            <div className="font-semibold">
                                {system.name}
                            </div>

                            <div className="text-sm text-gray-500">
                                {system.type}
                            </div>

                            <div
                                className="
                                    grid
                                    grid-cols-4
                                    gap-3
                                    mt-3
                                "
                            >

                                <div>
                                    <div className="text-xs text-gray-500">
                                        Leistung
                                    </div>

                                    <div className="font-medium">
                                        {system.peak_power_kw} kWp
                                    </div>
                                </div>

                                <div>
                                    <div className="text-xs text-gray-500">
                                        Strings
                                    </div>

                                    <div className="font-medium">
                                        {system.string_count}
                                    </div>
                                </div>

                                <div>
                                    <div className="text-xs text-gray-500">
                                        WR
                                    </div>

                                    <div className="font-medium">
                                        {system.inverter_power_kw ?? "-"} kW
                                    </div>
                                </div>

                                <div>
                                    <div className="text-xs text-gray-500">
                                        Speicher
                                    </div>

                                    <div className="font-medium">
                                        {system.battery_capacity_kwh ?? "-"} kWh
                                    </div>
                                </div>

                            </div>

                        </div>

                    ))}

                </div>

            </div>

        </div>
    );
}
