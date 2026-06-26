/*
# src/pages/DevicesPage.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { apiFetch } from "../api/client";
import { useStructure } from "../hooks/useStructure";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer
} from "recharts";


/* =========================================================
   DEVICE CARD
========================================================= */
function DeviceCard({ device, onSelect, onEdit }) {

    const config = device.config || {};
    const isOnline = device.status === "online";
    const missing = !config.measurement_type;

    function getIcon(roleKey) {
        switch (roleKey) {
            case "producer": return "⚡";
            case "consumer": return "🔌";
            case "battery": return "🔋";
            default: return "📦";
        }
    }

    return (
        <div
            onClick={() => onSelect(device)}
            className={`
                cursor-pointer
                border rounded-xl p-4 shadow-sm transition hover:shadow-md
                hover:ring-2 hover:ring-indigo-200
                ${missing
                    ? "border-yellow-300 bg-yellow-50"
                    : "border-gray-200 bg-white"
                }
            `}
        >

            <div className="flex justify-between mb-2 items-start">

                <div>
                    <div className="font-semibold flex items-center gap-2">
                        {getIcon(config.role?.key)}
                        {device.display_name}
                        {missing && <span className="text-yellow-600 text-sm">⚠</span>}
                    </div>

                    <div className="text-xs text-gray-400">
                        {device.identifier}
                    </div>
                </div>

                <div className="flex items-center gap-2 h-full">

                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onEdit(device);
                        }}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        ⚙️
                    </button>

                    <div className={`w-3 h-3 rounded-full ${isOnline ? "bg-green-500" : "bg-gray-300"
                        }`} />
                </div>
            </div>

            <div className="text-sm text-gray-500 mb-2">
                {config.role?.label || "–"}
            </div>

            <div className="text-xl font-bold text-indigo-600">
                {device.value != null
                    ? `${device.value} ${device.unit || ""}`
                    : "--"}
            </div>

            {missing && (
                <div className="text-xs text-yellow-600 mt-2">
                    ⚠ Messart fehlt
                </div>
            )}
        </div>
    );
}


/* =========================================================
   CHART MODAL ✅ NEU
========================================================= */
function DeviceChartModal({ device, onClose }) {

    const { data } = useQuery({
        queryKey: ["timeseries", device.id],
        queryFn: () =>
            apiFetch(`/api/devices/${device.id}/timeseries/?range=24h`)
    });

    const points = (data?.points || []).map(p => ({
        time: new Date(p.t * 1000).toLocaleTimeString(),
        value: p.v
    }));

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">

            <div className="bg-white p-6 rounded-xl w-full max-w-2xl">

                <h3 className="font-semibold mb-4">
                    {device.display_name}
                </h3>

                <div style={{ width: "100%", height: 300 }}>

                    <ResponsiveContainer>
                        <LineChart data={points}>

                            <XAxis dataKey="time" />
                            <YAxis />
                            <Tooltip />

                            <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#6366f1"
                                dot={false}
                            />

                        </LineChart>
                    </ResponsiveContainer>

                </div>

                <button
                    onClick={onClose}
                    className="mt-4 bg-gray-200 px-3 py-1 rounded"
                >
                    Schließen
                </button>

            </div>

        </div>
    );
}


/* =========================================================
   SETTINGS MODAL
========================================================= */
function DeviceSettingsModal({ device, onClose, refetch }) {

    const { data: structure } = useStructure();

    const roles = structure?.roles || [];
    const types = structure?.measurement_types || [];
    const rooms = structure?.rooms || [];
    const floors = structure?.floors || [];

    const [local, setLocal] = useState({
        name: device.config?.name || "",
        role_id: device.config?.role?.id || "",
        measurement_type: device.config?.measurement_type || "",
        room: device.config?.room?.id || "",
        floor: device.config?.floor?.id || "",
    });

    function update(field, value) {
        setLocal(prev => ({ ...prev, [field]: value }));
    }

    async function save() {
        await apiFetch(`/api/devices/${device.id}/`, {
            method: "PATCH",
            body: JSON.stringify(local),
        });

        await refetch();
        onClose();
    }

    async function remove() {
        if (!confirm("Gerät wirklich löschen?")) return;

        await apiFetch(`/api/devices/${device.id}/`, {
            method: "DELETE",
        });

        await refetch();
        onClose();
    }

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">

            <div className="bg-white p-6 rounded-xl w-full max-w-md">

                <h3 className="font-semibold mb-4">
                    Gerät bearbeiten
                </h3>

                <input
                    value={local.name}
                    onChange={(e) => update("name", e.target.value)}
                    className="w-full border rounded px-2 py-1 mb-3"
                    placeholder="Name"
                />

                <select
                    value={local.role_id}
                    onChange={(e) =>
                        update("role_id", e.target.value ? Number(e.target.value) : "")
                    }
                    className="w-full border rounded px-2 py-1 mb-3"
                >
                    <option value="">Rolle</option>
                    {roles.map(r => (
                        <option key={r.id} value={r.id}>
                            {r.label}
                        </option>
                    ))}
                </select>

                <select
                    value={local.measurement_type}
                    onChange={(e) => update("measurement_type", e.target.value)}
                    className="w-full border rounded px-2 py-1 mb-3"
                >
                    <option value="">Messart</option>
                    {types.map(t => (
                        <option key={t.key} value={t.key}>
                            {t.name}
                        </option>
                    ))}
                </select>

                <select
                    value={local.room}
                    onChange={(e) =>
                        update("room", e.target.value ? Number(e.target.value) : "")
                    }
                    className="w-full border rounded px-2 py-1 mb-3"
                >
                    <option value="">Raum</option>
                    {rooms.map(r => (
                        <option key={r.id} value={r.id}>
                            {r.name}
                        </option>
                    ))}
                </select>

                <select
                    value={local.floor}
                    onChange={(e) =>
                        update("floor", e.target.value ? Number(e.target.value) : "")
                    }
                    className="w-full border rounded px-2 py-1 mb-3"
                >
                    <option value="">Etage</option>
                    {floors.map(f => (
                        <option key={f.id} value={f.id}>
                            {f.name}
                        </option>
                    ))}
                </select>

                <div className="flex justify-between mt-4">

                    <button
                        onClick={remove}
                        className="text-red-600"
                    >
                        Löschen
                    </button>

                    <div className="flex gap-2">
                        <button
                            onClick={onClose}
                            className="bg-gray-200 px-3 py-1 rounded"
                        >
                            Abbrechen
                        </button>

                        <button
                            onClick={save}
                            className="bg-indigo-600 text-white px-3 py-1 rounded"
                        >
                            Speichern
                        </button>
                    </div>

                </div>

            </div>
        </div>
    );
}


/* =========================================================
   PAGE
========================================================= */
export default function DevicesPage() {

    const [chartDevice, setChartDevice] = useState(null);
    const [editingDevice, setEditingDevice] = useState(null);

    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
    });

    const statusQuery = useQuery({
        queryKey: ["devices-status"],
        queryFn: () => apiFetch("/api/devices/status/"),
        refetchInterval: 5000,
    });

    const valuesQuery = useQuery({
        queryKey: ["devices-values"],
        queryFn: () => apiFetch("/api/devices/latest/"),
        refetchInterval: 3000,
        retry: false,
    });

    const devices = devicesQuery.data || [];
    const statusList = statusQuery.data || [];
    const values = valuesQuery.data || [];

    const merged = devices.map(d => {
        const status = statusList.find(s => s.id === d.id);
        const value = values.find(v => v.device === d.id);

        return {
            ...d,
            status: status?.status || "offline",
            value: value?.value,
            unit: value?.unit,
        };
    });

    const grouped = merged
        .sort((a, b) => {
            const roomA = a.config?.room?.name || "";
            const roomB = b.config?.room?.name || "";

            if (roomA !== roomB) {
                return roomA.localeCompare(roomB);
            }

            return (a.display_name || "")
                .localeCompare(b.display_name || "");
        })
        .reduce((acc, d) => {
            const room = d.config?.room?.name || "Ohne Raum";
            acc[room] = acc[room] || [];
            acc[room].push(d);
            return acc;
        }, {});

    return (
        <div className="p-6 max-w-6xl">

            <h1 className="text-2xl font-semibold mb-6">
                Geräte
            </h1>

            {Object.entries(grouped)
                .sort(([a], [b]) => a.localeCompare(b))
                .map(([room, devices]) => (
                    <div key={room} className="mb-8">

                        <h2 className="text-sm text-gray-500 mb-3">
                            {room}
                        </h2>

                        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                            {devices.map(d => (
                                <DeviceCard
                                    key={d.id}
                                    device={d}
                                    onSelect={setChartDevice}
                                    onEdit={setEditingDevice}
                                />
                            ))}
                        </div>

                    </div>
                ))}

            {editingDevice && (
                <DeviceSettingsModal
                    device={editingDevice}
                    onClose={() => setEditingDevice(null)}
                    refetch={devicesQuery.refetch}
                />
            )}

            {chartDevice && (
                <DeviceChartModal
                    device={chartDevice}
                    onClose={() => setChartDevice(null)}
                />
            )}

        </div>
    );
}
