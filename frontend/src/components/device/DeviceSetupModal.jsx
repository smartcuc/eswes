/*
# src/components/device/DeviceSetupModal.jsx
*/

import { useState, useEffect } from "react";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";
import {
    useDeviceTypes,
    useDeviceRoles,
    useMeasurementTypes
} from "../../hooks/useDeviceMeta";
import {
    useHomes,
    useFloors,
    useRooms
} from "../../hooks/useStructure";
import { apiFetch } from "../../api/client";

export default function DeviceSetupModal({ open, onClose }) {

    const query = useUnconfiguredDevices();
    const devices = query?.data?.devices || [];
    const isLoading = query?.isLoading;

    const types = useDeviceTypes().data || [];
    const roles = useDeviceRoles().data || [];
    const measurementTypes = useMeasurementTypes().data || [];

    const homes = useHomes().data || [];
    const floors = useFloors().data || [];
    const rooms = useRooms().data || [];

    const [localValues, setLocalValues] = useState({});
    const [saving, setSaving] = useState({});
    const [saved, setSaved] = useState({});
    const [page, setPage] = useState(0);

    const PAGE_SIZE = 5;

    const paginatedDevices = devices.slice(
        page * PAGE_SIZE,
        (page + 1) * PAGE_SIZE
    );

    // ✅ FIXED CHANGE HANDLER
    function handleChange(id, field, value) {
        setLocalValues((prev) => ({
            ...prev,
            [id]: {
                ...prev[id],
                [field]: value,
            },
        }));
    }

    async function handleSave(device) {
        const values = localValues[device.id];
        if (!values) return;

        setSaving((prev) => ({ ...prev, [device.id]: true }));

        await apiFetch(`/api/devices/${device.id}/`, {
            method: "PATCH",
            body: JSON.stringify(values),
        });

        setSaving((prev) => ({ ...prev, [device.id]: false }));
        setSaved((prev) => ({ ...prev, [device.id]: true }));

        setTimeout(() => {
            setSaved((prev) => ({ ...prev, [device.id]: false }));
        }, 1200);

        await query.refetch();
    }

    async function handleSaveAll() {
        const updates = Object.entries(localValues);

        for (const [id, values] of updates) {
            if (!values) continue;

            await apiFetch(`/api/devices/${id}/`, {
                method: "PATCH",
                body: JSON.stringify(values),
            });
        }

        await query.refetch();
    }

    // ✅ RESET
    useEffect(() => {
        if (open) {
            setLocalValues({});
            setSaving({});
            setSaved({});
            setPage(0);
        }
    }, [open]);

    // ✅ PROGRESS
    const completed = devices.filter(d =>
        d.type?.key &&
        d.role?.key &&
        d.room?.id
    ).length;

    const total = devices.length;
    const percent = total ? Math.round((completed / total) * 100) : 0;

    // ✅ AUTO CLOSE
    useEffect(() => {
        if (!isLoading && total > 0 && completed === total) {
            const t = setTimeout(() => onClose(), 900);
            return () => clearTimeout(t);
        }
    }, [completed, total, isLoading, onClose]);

    if (!open) return null;

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">

            <div className="bg-white rounded-xl shadow-lg w-full max-w-6xl p-6">

                {/* HEADER */}
                <div className="flex justify-between mb-4">
                    <div>
                        <h2 className="text-lg font-semibold">
                            ⚡ Geräte konfigurieren
                        </h2>
                        <p className="text-sm text-gray-500">
                            Funktion & Standort festlegen
                        </p>
                    </div>

                    <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                        ✕
                    </button>
                </div>

                {/* PROGRESS */}
                {!isLoading && total > 0 && (
                    <div className="mb-4">
                        <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>{completed} / {total}</span>
                            <span>{percent}%</span>
                        </div>
                        <div className="h-2 bg-gray-100 rounded overflow-hidden">
                            <div
                                className="h-2 bg-indigo-500 transition-all duration-500"
                                style={{ width: `${percent}%` }}
                            />
                        </div>
                    </div>
                )}

                {/* ACTIONS */}
                <div className="flex justify-between mb-4">
                    <span className="text-xs text-gray-400">
                        Änderungen werden erst beim Speichern übernommen
                    </span>

                    <button
                        onClick={handleSaveAll}
                        className="bg-indigo-600 text-white px-3 py-1 rounded text-sm hover:bg-indigo-700"
                    >
                        Save all
                    </button>
                </div>

                {/* CONTENT */}
                <div className="space-y-3 max-h-[450px] overflow-auto">

                    {isLoading && (
                        <div className="text-sm text-gray-500">
                            Lade Geräte...
                        </div>
                    )}

                    {!isLoading && paginatedDevices.map((device, index) => {

                        const local = localValues[device.id] || {};
                        const isComplete =
                            (local.type || device.type?.key) &&
                            (local.role || device.role?.key) &&
                            (local.room || device.room?.id);

                        return (

                            <div
                                key={device.id}
                                className={`p-4 border rounded-lg transition hover:shadow ${isComplete
                                        ? "bg-green-50 border-green-200"
                                        : index % 2 === 0
                                            ? "bg-gray-50"
                                            : "bg-white"
                                    }`}
                            >

                                {/* NAME + STATUS */}
                                <div className="flex justify-between items-center mb-4">
                                    <div className="text-sm font-medium">
                                        {device.name || `Device ${device.id}`}
                                    </div>

                                    <span className={`text-xs px-2 py-0.5 rounded-full ${isComplete
                                            ? "bg-green-100 text-green-700"
                                            : "bg-yellow-100 text-yellow-700"
                                        }`}>
                                        {isComplete ? "Fertig" : "Offen"}
                                    </span>
                                </div>

                                {/* ✅ FUNKTION */}
                                <div className="mb-3">
                                    <div className="flex items-center gap-2 text-xs text-gray-400 mb-1 uppercase">
                                        ⚡ Funktion
                                    </div>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">

                                        <select
                                            value={local.type ?? device.type?.key ?? ""}
                                            onChange={(e) =>
                                                handleChange(device.id, "type", e.target.value)
                                            }
                                            className="border rounded px-2 py-1 text-sm w-full"
                                        >
                                            <option value="">⚙️ Type</option>
                                            {types.map(t => (
                                                <option key={t.key} value={t.key}>
                                                    {t.name}
                                                </option>
                                            ))}
                                        </select>

                                        <select
                                            value={local.role ?? device.role?.key ?? ""}
                                            onChange={(e) =>
                                                handleChange(device.id, "role", e.target.value)
                                            }
                                            className="border rounded px-2 py-1 text-sm w-full"
                                        >
                                            <option value="">🔁 Role</option>
                                            {roles.map(r => (
                                                <option key={r.key} value={r.key}>
                                                    {r.name}
                                                </option>
                                            ))}
                                        </select>

                                        <select
                                            value={
                                                local.measurement_type ??
                                                device.measurement_type ??
                                                ""
                                            }
                                            onChange={(e) =>
                                                handleChange(device.id, "measurement_type", e.target.value)
                                            }
                                            className="border rounded px-2 py-1 text-sm w-full"
                                        >
                                            <option value="">📏 Messart</option>
                                            {measurementTypes.map(m => (
                                                <option key={m.key} value={m.key}>
                                                    {m.name}
                                                </option>
                                            ))}
                                        </select>

                                    </div>
                                </div>

                                {/* ✅ STANDORT */}
                                <div className="mb-3">
                                    <div className="flex items-center gap-2 text-xs text-gray-400 mb-1 uppercase">
                                        📍 Standort
                                    </div>

                                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">

                                        {homes.length > 1 && (
                                            <select
                                                value={local.home ?? device.home?.id ?? ""}
                                                onChange={(e) =>
                                                    handleChange(device.id, "home", e.target.value)
                                                }
                                                className="border rounded px-2 py-1 text-sm w-full"
                                            >
                                                <option value="">🏠 Home</option>
                                                {homes.map(h => (
                                                    <option key={h.id} value={h.id}>
                                                        {h.name}
                                                    </option>
                                                ))}
                                            </select>
                                        )}

                                        <select
                                            value={local.floor ?? device.floor?.id ?? ""}
                                            onChange={(e) =>
                                                handleChange(device.id, "floor", e.target.value)
                                            }
                                            className="border rounded px-2 py-1 text-sm w-full"
                                        >
                                            <option value="">🏢 Etage</option>
                                            {floors.map(f => (
                                                <option key={f.id} value={f.id}>
                                                    {f.name}
                                                </option>
                                            ))}
                                        </select>

                                        <select
                                            value={local.room ?? device.room?.id ?? ""}
                                            onChange={(e) =>
                                                handleChange(device.id, "room", e.target.value)
                                            }
                                            className="border rounded px-2 py-1 text-sm w-full"
                                        >
                                            <option value="">🚪 Raum</option>
                                            {rooms.map(r => (
                                                <option key={r.id} value={r.id}>
                                                    {r.name}
                                                </option>
                                            ))}
                                        </select>

                                        {/* SAVE */}
                                        <button
                                            onClick={() => handleSave(device)}
                                            disabled={saving[device.id]}
                                            className={`w-full px-3 py-1 text-sm rounded transform transition ${saving[device.id]
                                                    ? "bg-gray-200 text-gray-500"
                                                    : "bg-indigo-600 text-white hover:bg-indigo-700 hover:scale-105 active:scale-95"
                                                }`}
                                        >
                                            {saving[device.id]
                                                ? "..."
                                                : saved[device.id]
                                                    ? "✔"
                                                    : "Save"}
                                        </button>

                                    </div>

                                    {saved[device.id] && (
                                        <div className="text-xs text-green-600 mt-1">
                                            ✓ gespeichert
                                        </div>
                                    )}

                                </div>

                            </div>
                        );
                    })}

                </div>

                {/* PAGINATION */}
                {!isLoading && total > PAGE_SIZE && (
                    <div className="flex justify-between mt-4 text-sm">
                        <button
                            disabled={page === 0}
                            onClick={() => setPage(p => p - 1)}
                        >
                            ←
                        </button>

                        <span>{page + 1} / {Math.ceil(total / PAGE_SIZE)}</span>

                        <button
                            disabled={(page + 1) * PAGE_SIZE >= total}
                            onClick={() => setPage(p => p + 1)}
                        >
                            →
                        </button>
                    </div>
                )}

                {/* FOOTER */}
                <div className="mt-6 flex justify-end">
                    <button
                        onClick={onClose}
                        className="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700"
                    >
                        Fertig
                    </button>
                </div>

            </div>
        </div>
    );
}
