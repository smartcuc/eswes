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

    const getSortName = d =>
        (d.display_name || d.identifier || "").toLowerCase().trim();

    const devices = (isBulk
        ? bulkDevices
        : singleDevice ? [singleDevice] : []
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
    const [serverDevices, setServerDevices] = useState({});

    const debounceTimers = useRef({});

    /* ================================
       ✅ WEBSOCKET
    ================================= */
    useEffect(() => {
        const protocol = window.location.protocol === "https:" ? "wss" : "ws";
        const socket = new WebSocket(`${protocol}://${window.location.host}/ws/energy/`);

        socket.onmessage = (event) => {
            const data = JSON.parse(event.data);

            if (data.type === "device_update" && data.device) {
                setServerDevices(prev => ({
                    ...prev,
                    [data.device.id]: data.device
                }));
            }
        };

        return () => socket.close();
    }, []);

    /* ================================
       ✅ ESC SUPPORT
    ================================= */
    useEffect(() => {
        function onKey(e) {
            if (e.key === "Escape") {
                onClose();
            }
        }

        window.addEventListener("keydown", onKey);
        return () => window.removeEventListener("keydown", onKey);
    }, [onClose]);

    /* ================================
       ✅ SAVE (FIXED)
    ================================= */
    async function saveDevice(id, values) {

        if (!values || Object.keys(values).length === 0) return;

        const key = String(id);

        setSaving(prev => ({
            ...prev,
            [key]: true
        }));

        setError(prev => ({
            ...prev,
            [key]: false
        }));

        try {
            const data = await apiFetch(`/api/devices/${id}/`, {
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

            // ✅ Server-Update mergen
            if (data && data.device) {
                setServerDevices(prev => ({
                    ...prev,
                    [data.device.id]: data.device
                }));

                // ✅ local zurücksetzen → entfernt gelben Zustand
                setLocalValues(prev => {
                    const copy = { ...prev };
                    delete copy[key];
                    return copy;
                });
            }

            setSaving(prev => ({
                ...prev,
                [key]: false
            }));

            setSaved(prev => ({
                ...prev,
                [key]: true
            }));

            setTimeout(() => {
                setSaved(prev => ({
                    ...prev,
                    [key]: false
                }));
            }, 1200);

            // ✅ wichtig für "reopen zeigt alten Wert"-Bug
            if (query?.refetch) {
                query.refetch();
            }

        } catch (err) {
            console.error("save failed", err);

            setSaving(prev => ({
                ...prev,
                [key]: false
            }));

            setError(prev => ({
                ...prev,
                [key]: true
            }));
        }
    }

    /* ================================
       ✅ CHANGE
    ================================= */
    function handleChange(id, field, value) {

        const key = String(id);

        setLocalValues(prev => {
            const deviceValues = { ...(prev[key] || {}) };
            deviceValues[field] = value;

            const updated = {
                ...prev,
                [key]: deviceValues
            };

            if (field === "display_name") {

                if (debounceTimers.current[key]) {
                    clearTimeout(debounceTimers.current[key]);
                }

                debounceTimers.current[key] = setTimeout(() => {
                    saveDevice(id, deviceValues);
                }, 600);

            } else {
                saveDevice(id, deviceValues);
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
       RESET
    ================================= */

    useEffect(() => {
        if (open) {
            setLocalValues({});
            setSaving({});
            setSaved({});
            setError({});
            setServerDevices({});
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
                    <button onClick={onClose}>✕</button>
                </div>

                {/* CONTENT */}
                <div className="space-y-3 max-h-[450px] overflow-auto">

                    {!isLoading && devices.map(device => {

                        const key = String(device.id);
                        const local = localValues[key] || {};
                        const server = serverDevices[key] || device;

                        const displayName =
                            local.display_name ??
                            server.display_name ??
                            device.display_name ?? "";

                        const roleId =
                            local.role_id ??
                            server.config?.role?.id ??
                            device.config?.role?.id ?? "";

                        const measurementType =
                            local.measurement_type ??
                            server.config?.measurement_type ??
                            device.config?.measurement_type ?? "";

                        const floorId =
                            local.floor_id ??
                            server.config?.floor?.id ??
                            device.config?.floor?.id ?? "";

                        const roomId =
                            local.room_id ??
                            server.config?.room?.id ??
                            device.config?.room?.id ?? "";

                        const homeId =
                            local.home_id ??
                            server.config?.home?.id ??
                            device.config?.home?.id ?? "";

                        const hasChanges = Object.keys(local).length > 0;

                        return (
                            <div
                                key={key}
                                className={`p-4 border rounded-lg
                                ${hasChanges ? "bg-yellow-50 border-yellow-200" : ""}
                                ${saved[key] ? "bg-green-50 border-green-200" : ""}
                            `}>

                                {/* HEADER */}
                                <div className="flex justify-between items-center mb-2">
                                    <div className="font-medium">{displayName}</div>
                                    <div className="flex gap-2">
                                        {saving[key] && <span>⏳</span>}
                                        {saved[key] && <span>✅</span>}
                                        {error[key] && (
                                            <span onClick={() => handleRetry(device.id)} className="cursor-pointer">❌</span>
                                        )}
                                    </div>
                                </div>

                                {/* NAME */}
                                <input
                                    value={displayName}
                                    onChange={(e) =>
                                        handleChange(device.id, "display_name", e.target.value)
                                    }
                                    className="border px-2 py-1 w-full mb-3 rounded"
                                />

                                {/* ROLE */}
                                <select
                                    value={roleId}
                                    onChange={(e) =>
                                        handleChange(device.id, "role_id", e.target.value ? Number(e.target.value) : null)
                                    }
                                    className="border px-2 py-1 w-full mb-3 rounded"
                                >
                                    <option value="">Rolle</option>
                                    {roles.map(r => (
                                        <option key={r.id} value={r.id}>{r.label}</option>
                                    ))}
                                </select>

                                {/* MEASUREMENT */}
                                <select
                                    value={measurementType || ""}
                                    onChange={(e) =>
                                        handleChange(device.id, "measurement_type", e.target.value || null)
                                    }
                                    className="border px-2 py-1 w-full mb-3 rounded"
                                >
                                    <option value="">Messung</option>
                                    {measurementTypes.map(m => (
                                        <option key={m.key || m.id} value={m.key || m.value}>
                                            {m.label || m.name}
                                        </option>
                                    ))}
                                </select>

                                {/* LOCATION */}
                                <div className="grid grid-cols-1 sm:grid-cols-4 gap-3">

                                    {hasMultipleHomes && (
                                        <select
                                            value={homeId}
                                            onChange={(e) =>
                                                handleChange(device.id, "home_id", e.target.value ? Number(e.target.value) : null)
                                            }
                                            className="border px-2 py-1 rounded"
                                        >
                                            <option value="">🏠 Zuhause</option>
                                            {homes.map(h => (
                                                <option key={h.id} value={h.id}>{h.name}</option>
                                            ))}
                                        </select>
                                    )}

                                    <select
                                        value={floorId}
                                        onChange={(e) =>
                                            handleChange(device.id, "floor_id", e.target.value ? Number(e.target.value) : null)
                                        }
                                        className="border px-2 py-1 rounded"
                                    >
                                        <option value="">🏢 Etage</option>
                                        {floors.map(f => (
                                            <option key={f.id} value={f.id}>{f.name}</option>
                                        ))}
                                    </select>

                                    <select
                                        value={roomId}
                                        onChange={(e) =>
                                            handleChange(device.id, "room_id", e.target.value ? Number(e.target.value) : null)
                                        }
                                        className="border px-2 py-1 rounded"
                                    >
                                        <option value="">🚪 Raum</option>
                                        {rooms.map(r => (
                                            <option key={r.id} value={r.id}>{r.name}</option>
                                        ))}
                                    </select>

                                </div>

                            </div>
                        );
                    })}

                </div>

                {/* FOOTER */}
                <div className="mt-6 flex justify-end border-t pt-4">
                    <button
                        onClick={onClose}
                        className="bg-indigo-600 hover:bg-indigo-700 text-white px-5 py-2 rounded-lg"
                    >
                        {isBulk ? "Fertig" : "Schließen"}
                    </button>
                </div>

            </div>
        </div>
    );
}