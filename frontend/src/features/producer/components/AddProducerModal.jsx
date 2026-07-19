/*
# src/features/producer/components/AddProducerModal.jsx
*/

import { useState } from "react";
import { apiFetch } from "../../../api/client";
import { useQuery } from "@tanstack/react-query";
import { getGeneratorTypes } from "../api";

export default function AddProducerModal({
    open,
    onClose,
    onCreated,
}) {

    // const [generatorType, setGeneratorType] =
    //     useState("");

    const { data: generatorTypes = [] } =
        useQuery({
            queryKey: ["generator-types"],
            queryFn: getGeneratorTypes,
        });

    const [generatorType, setGeneratorType] = useState("");

    const [name, setName] = useState("");

    const [peakPower, setPeakPower] =
        useState("");

    const [inverterPower, setInverterPower] =
        useState("");

    const [batteryCapacity, setBatteryCapacity] =
        useState("");

    async function handleSave() {

        await apiFetch(
            "/api/producer/create/",
            {
                method: "POST",

                body: JSON.stringify({

                    name,

                    generator_type:
                        generatorType,

                    peak_power_kw:
                        peakPower,

                    inverter_power_kw:
                        inverterPower,

                    battery_capacity_kwh:
                        batteryCapacity,

                }),

            }
        );

        onCreated();
        onClose();
    }

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
                    rounded-xl
                    p-6
                    w-full
                    max-w-lg
                "
                onClick={(e) =>
                    e.stopPropagation()
                }
            >

                <h2 className="text-lg font-semibold mb-4">
                    ☀️ Erzeuger anlegen
                </h2>

                <div className="space-y-3">

                    <input
                        value={name}
                        onChange={(e) =>
                            setName(e.target.value)
                        }
                        placeholder="Name"
                        className="w-full border rounded p-2"
                    />

                    <select
                        value={generatorType}
                        onChange={(e) =>
                            setGeneratorType(
                                e.target.value
                            )
                        }
                        className="w-full border rounded p-2"
                    >

                        <option value="">
                            Typ auswählen
                        </option>

                        {generatorTypes.map((type) => (

                            <option
                                key={type.id}
                                value={type.id}
                            >
                                {type.name}
                            </option>

                        ))}

                    </select>

                    <input
                        value={peakPower}
                        onChange={(e) =>
                            setPeakPower(e.target.value)
                        }
                        placeholder="Leistung (kWp)"
                        className="w-full border rounded p-2"
                    />

                    <input
                        value={inverterPower}
                        onChange={(e) =>
                            setInverterPower(e.target.value)
                        }
                        placeholder="WR Leistung (kW)"
                        className="w-full border rounded p-2"
                    />

                    <input
                        value={batteryCapacity}
                        onChange={(e) =>
                            setBatteryCapacity(
                                e.target.value
                            )
                        }
                        placeholder="Speicher (kWh)"
                        className="w-full border rounded p-2"
                    />

                </div>

                <div className="flex justify-end gap-2 mt-5">

                    <button
                        onClick={onClose}
                        className="
                            px-4 py-2
                            border rounded
                        "
                    >
                        Abbrechen
                    </button>

                    <button
                        onClick={handleSave}
                        className="
                            px-4 py-2
                            bg-amber-500
                            text-white
                            rounded
                        "
                    >
                        Speichern
                    </button>

                </div>

            </div>

        </div>
    );
}
