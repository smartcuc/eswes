/*
# src/components/DeviceSetupModal.jsx
*/

import React from "react";
import { apiFetch } from "../api/client";

export default function DeviceSetupModal({ devices, onClose, onSaved }) {

    const [form, setForm] = React.useState({});

    const update = (id, field, value) => {
        setForm((prev) => ({
            ...prev,
            [id]: {
                ...prev[id],
                [field]: value,
            },
        }));
    };

    const save = async () => {
        try {
            for (const id of Object.keys(form)) {

                await apiFetch(`/api/energy/devices/${id}/configure/`, {
                    method: "POST",
                    body: JSON.stringify(form[id]),
                });

            }

            onSaved();

        } catch (err) {
            console.error("Device setup failed:", err);
        }
    };

    return (
        <div className="fixed inset-0 bg-black/40 flex justify-center items-center">
            <div className="bg-white w-[500px] p-6 rounded-2xl">
                <h2 className="text-xl mb-4">Neue Geräte konfigurieren</h2>

                {devices.map((d) => (
                    <div key={d.id} className="mb-6 border-b pb-4">
                        <div className="font-semibold">{d.name}</div>

                        {/* Rolle */}
                        <select
                            className="mt-2 w-full border p-2"
                            onChange={(e) => update(d.id, "role", e.target.value)}
                        >
                            <option value="">Rolle wählen</option>
                            <option value="pv">PV</option>
                            <option value="load">Verbrauch</option>
                            <option value="battery">Batterie</option>
                            <option value="grid">Netz</option>
                        </select>

                        {/* Raum */}
                        <input
                            className="mt-2 w-full border p-2"
                            placeholder="Raum (z. B. Wohnzimmer)"
                            onChange={(e) => update(d.id, "room", e.target.value)}
                        />
                    </div>
                ))}

                <div className="flex justify-end gap-2">
                    <button onClick={onClose}>Abbrechen</button>
                    <button
                        onClick={save}
                        className="bg-black text-white px-4 py-2 rounded"
                    >
                        Speichern
                    </button>
                </div>
            </div>
        </div>
    );
}

