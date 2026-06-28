/*
# src/components/device/DeviceSetupModal.jsx
*/

import { useState, useEffect, useRef } from "react";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";
import { useSettings } from "../../hooks/useSettings";
import { useStructure } from "../../hooks/useStructure";
import { apiFetch } from "../../api/client";

export default function DeviceSetupModal({ open, onClose, mode = "bulk", singleDevice = null }) {

    const isBulk = mode === "bulk";

    const query = useUnconfiguredDevices();
    const bulkDevices = query?.data?.devices || [];
    const isLoading = query?.isLoading;

    /* ✅ Gerätequelle */

    const getSortName = d =>
        (d.display_name || d.identifier || "").toLowerCase().trim();

    const devices = (isBulk
        ? bulkDevices
        : singleDevice
            ? [singleDevice]
            : []
    ).slice().sort((a, b) => getSortName(a).localeCompare(getSortName(b)));


    const { settings } = useSettings();
    const homes = settings?.homes || [];
    const hasMultipleHomes = homes.length > 1;

    const { data: structure } = useStructure();

    const roles = structure?.roles || [];
    const measurementTypes = structure?.measurement_types || [];
    const floors = structure?.floors || [];
    const rooms = structure?.rooms || [];

    const [localValues, setLocalValues] = useState({});
    const [saving, setSaving] = useState({});
    const [saved, setSaved] = useState({});
    const [error, setError] = useState({});

    const debounceTimers = useRef({});

    /* ================================
       SAVE (Bulk = Auto, Single = Manual vorbereitet)
    ================================= */

    async function saveDevice(id, values) {

        if (!values || Object.keys(values).length === 0) return;

        const key = String(id);

        setSaving(prev => {
            const copy = { ...prev };
            copy[key] = true;
            return copy;
        });

        setError(prev => {
            const copy = { ...prev };
            copy[key] = false;
            return copy;
        });

        try {
            await apiFetch("/api/devices/" + id + "/", {
                method: "PATCH",

                body: JSON.stringify({
                    display_name: values.display_name,
                    role_id: values.role_id,
                    measurement_type: values.measurement_type,
                    room_id: values.room_id,
                    floor_id: values.floor_id,
                    home_id: values.home_id,
                })

            });

            setSaving(prev => {
                const copy = { ...prev };
                copy[key] = false;
                return copy;
            });

            setSaved(prev => {
                const copy = { ...prev };
                copy[key] = true;
                return copy;
            });

            setTimeout(() => {
                setSaved(prev => {
                    const copy = { ...prev };
                    copy[key] = false;
                    return copy;
                });
            }, 1200);

            /* ✅ Highlight reset nach Erfolg */
            setLocalValues(prev => {
                const copy = { ...prev };
                delete copy[key];
                return copy;
            });

        } catch (err) {
            console.error("save failed", err);

            setSaving(prev => {
                const copy = { ...prev };
                copy[key] = false;
                return copy;
            });

            setError(prev => {
                const copy = { ...prev };
                copy[key] = true;
                return copy;
            });
        }
    }

    /* ================================
       CHANGE
    ================================= */

    function handleChange(id, field, value) {

        const key = String(id);

        setLocalValues(prev => {

            const deviceValues = { ...(prev[key] || {}) };
            deviceValues[field] = value;

            const updated = { ...prev };
            updated[key] = deviceValues;

            /* ✅ Autosave nur im Bulk Mode */

            if (isBulk) {

                if (debounceTimers.current[key]) {
                    clearTimeout(debounceTimers.current[key]);
                }

                debounceTimers.current[key] = setTimeout(() => {
                    setLocalValues(prevState => {

                        const values = prevState[key];

                        if (values) {
                            saveDevice(id, values);
                        }

                        return prevState;
                    });

                }, 600);
            }
            return updated;
        });
    }

    function handleRetry(id) {
        const key = String(id);
        if (localValues[key]) {
            saveDevice(id, localValues[key]);
        }
    }

    /* ================================
       SINGLE SAVE (vorbereitet)
    ================================= */

    async function handleSaveSingle() {
        const ids = Object.keys(localValues);
        for (let i = 0; i < ids.length; i++) {
            const id = ids[i];
            await saveDevice(id, localValues[id]);
        }
    }

    /* ================================
       RESET
    ================================= */

    useEffect(() => {
        if (open) {
            setLocalValues({});
            setSaving({});
            setSaved({});
            setError({});
        }
    }, [open]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl shadow-lg w-full max-w-6xl p-6">

                {/* HEADER */}
                <div className="flex justify-between mb-4">
                    <div>
                        <h2 className="text-lg font-semibold">
                            {isBulk ? "⚡ Geräte konfigurieren" : "Gerät bearbeiten"}
                        </h2>
                        <p className="text-sm text-gray-500">
                            Funktion & Standort festlegen
                        </p>
                    </div>
                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-lg">✕</button>
                </div>

                {/* CONTENT */}
                <div className="space-y-3 max-h-[450px] overflow-auto">

                    {!isLoading && devices.map((device) => {

                        const key = String(device.id);
                        const local = localValues[key] || {};
                        const hasChanges = Object.keys(local).length > 0;

                        return (
                            <div
                                key={device.id}
                                className={`p-4 border rounded-lg transition-all duration-300
                                ${hasChanges ? "bg-yellow-50 border-yellow-200" : ""}
                                ${saved[key] ? "bg-green-50 border-green-200 ring-1 ring-green-200" : ""}
                            `}
                            >

                                {/* HEADER */}
                                <div className="flex justify-between items-center mb-3">

                                    <div className="font-medium flex items-center">
                                        {device.display_name}

                                        {hasChanges && !saving[key] && (
                                            <span className="text-xs text-yellow-600 ml-2">
                                                ● geändert
                                            </span>
                                        )}
                                    </div>

                                    {/* STATUS (wird bei Bulk direkt in der Zeile angezeigt) */}
                                    {isBulk && (
                                        <div className="text-sm flex items-center gap-2 min-w-[60px] justify-end">
                                            {saving[key] && <span className="animate-pulse">⏳</span>}
                                            {saved[key] && "✅"}
                                            {error[key] && (
                                                <span
                                                    onClick={() => handleRetry(device.id)}
                                                    className="cursor-pointer"
                                                    title="Erneut versuchen"
                                                >
                                                    ❌
                                                </span>
                                            )}
                                        </div>
                                    )}

                                </div>

                                {/* NAME */}
                                <input
                                    value={local.display_name ?? device.display_name}
                                    onChange={(e) =>
                                        handleChange(device.id, "display_name", e.target.value)
                                    }
                                    className="border px-2 py-1 w-full mb-3 rounded"
                                />

                                {/* ROLE */}
                                <select
                                    value={local.role_id ?? device.config?.role?.id ?? ""}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "role_id",
                                            e.target.value ? Number(e.target.value) : null
                                        )
                                    }
                                    className="border px-2 py-1 w-full mb-3 rounded"
                                >
                                    <option value="">Rolle</option>
                                    {roles.map(r => (
                                        <option key={r.id} value={r.id}>{r.label}</option>
                                    ))}
                                </select>


                                {/* LOCATION */}
                                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">

                                    {/* Zuhause-Auswahl */}
                                    {hasMultipleHomes && (
                                        <select
                                            value={local.home_id ?? device.config?.home?.id ?? ""}
                                            onChange={(e) =>
                                                handleChange(
                                                    device.id,
                                                    "home_id",
                                                    e.target.value ? Number(e.target.value) : null
                                                )
                                            }
                                            className="border px-2 py-1 w-full rounded"
                                        >
                                            <option value="">🏠 Zuhause</option>
                                            {homes.map(h => (
                                                <option key={h.id} value={h.id}>
                                                    {h.name}
                                                </option>
                                            ))}
                                        </select>
                                    )}

                                    {/* Etagen-Auswahl */}
                                    <select
                                        value={local.floor_id ?? device.config?.floor?.id ?? ""}
                                        onChange={(e) =>
                                            handleChange(
                                                device.id,
                                                "floor_id",
                                                e.target.value ? Number(e.target.value) : null
                                            )
                                        }
                                        className="border px-2 py-1 w-full rounded"
                                    >
                                        <option value="">🏢 Etage</option>
                                        {floors.map(f => (
                                            <option key={f.id} value={f.id}>
                                                {f.name}
                                            </option>
                                        ))}
                                    </select>

                                    {/* Raum-Auswahl */}
                                    <select
                                        value={local.room_id ?? device.config?.room?.id ?? ""}
                                        onChange={(e) =>
                                            handleChange(
                                                device.id,
                                                "room_id",
                                                e.target.value ? Number(e.target.value) : null
                                            )
                                        }
                                        className="border px-2 py-1 w-full rounded"
                                    >
                                        <option value="">🚪 Raum</option>
                                        {rooms.map(r => (
                                            <option key={r.id} value={r.id}>
                                                {r.name}
                                            </option>
                                        ))}
                                    </select>

                                </div>

                                {/* INLINE-STATUS FÜR EINZELGERÄT */}
                                {!isBulk && hasChanges && (
                                    <div className="mt-3 flex justify-end items-center gap-2 text-sm text-gray-500">
                                        {saving[key] && <span>⏳ Speichert im Hintergrund...</span>}
                                        {saved[key] && <span className="text-green-600">✅ Gespeichert</span>}
                                        {error[key] && (
                                            <button
                                                onClick={() => handleRetry(device.id)}
                                                className="text-red-600 underline font-medium"
                                            >
                                                ❌ Fehler. Erneut versuchen?
                                            </button>
                                        )}
                                    </div>
                                )}

                            </div>
                        );
                    })}

                </div>

                {/* MODAL GLOBAL FOOTER */}
                <div className="mt-6 flex justify-end gap-2 border-t pt-4">
                    <button
                        onClick={onClose}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg font-medium transition"
                    >
                        {isBulk ? "Fertig" : "Schließen"}
                    </button>
                </div>

            </div>
        </div>
    );
}

