/*
# src/features/producer/components/AddStringModal.jsx
*/

import { useState } from "react";
import { apiFetch } from "../../../api/client";
import { useQuery } from "@tanstack/react-query";
import { getOrientations } from "../api";


function normalizeDecimal(value) {
    return value
        ?.toString()
        .replace(",", ".");
}


export default function AddStringModal({
    open,
    onClose,
    generatorId,
    onCreated,
}) {

    const [name, setName] =
        useState("");

    const [modules, setModules] =
        useState("");

    const [power, setPower] =
        useState("");

    const { data: orientations = [] } =
        useQuery({
            queryKey: ["orientations"],
            queryFn: getOrientations,
        });

    const [orientationId, setOrientationId] = useState("");

    const [tilt, setTilt] =
        useState(35);

    async function handleSave() {

        await apiFetch(
            "/api/producer/string/create/",
            {
                method: "POST",

                body: JSON.stringify({
                    generator_id:
                        generatorId,

                    name,

                    module_count:
                        Number(modules),

                    peak_power_kwp:
                        normalizeDecimal(power),

                    orientation_id:
                        orientationId,

                    tilt_deg:
                        Number(tilt),
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
                    String hinzufügen
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
                        value={orientationId}
                        onChange={(e) =>
                            setOrientationId(
                                e.target.value
                            )
                        }
                        className="w-full border rounded p-2"
                    >

                        <option value="">
                            Ausrichtung auswählen
                        </option>

                        {orientations.map((orientation) => (

                            <option
                                key={orientation.id}
                                value={orientation.id}
                            >
                                {orientation.name}
                            </option>

                        ))}

                    </select>

                    <input
                        value={modules}
                        onChange={(e) =>
                            setModules(e.target.value)
                        }
                        placeholder="Module"
                        className="w-full border rounded p-2"
                    />

                    <input
                        value={power}
                        onChange={(e) =>
                            setPower(e.target.value)
                        }
                        placeholder="Leistung (kWp)"
                        className="w-full border rounded p-2"
                    />

                    <input
                        value={tilt}
                        onChange={(e) =>
                            setTilt(
                                e.target.value
                            )
                        }
                        placeholder="Neigung"
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
