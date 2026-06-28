/*
# src/pages/DevicesPage.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { apiFetch } from "../api/client";
import { useStructure } from "../hooks/useStructure";
import DeviceChartModal from "../components/device/DeviceChartModal";
import DeviceSetupModal from "../components/device/DeviceSetupModal";


/* =========================================================
   DEVICE CARD
========================================================= */
function DeviceCard({ device, onSelect, onEdit }) {

    const config = device.config || {};
    const isOnline = device.status === "online";
    const missing = !config.measurement_type || !config.role;

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
                        className="text-gray-400 hover:text-gray-600 relative group"
                    >
                        ⚙️
                        <span className="absolute bottom-full mb-1 hidden group-hover:block text-xs bg-gray-800 text-white px-2 py-1 rounded whitespace-nowrap">
                            Gerät bearbeiten
                        </span>
                    </button>

                    <div className="relative group">
                        <div
                            className={`w-3 h-3 rounded-full ${isOnline ? "bg-green-500" : "bg-gray-300"
                                }`}
                        />
                        <span className="absolute bottom-full mb-1 hidden group-hover:block text-xs bg-gray-800 text-white px-2 py-1 rounded whitespace-nowrap">
                            {isOnline ? "Online" : "Offline"}
                        </span>
                    </div>

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

    const unconfiguredDevices = merged.filter(d => {
        const config = d.config || {};
        return !config.measurement_type || !config.room;
    });

    const grouped = merged
        .slice()   // ✅ wichtig!
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

            {unconfiguredDevices.length > 0 && (
                <div className="mb-6 p-4 rounded-lg border border-yellow-300 bg-yellow-50 flex items-center justify-between">

                    <div className="text-yellow-800 text-sm">
                        ⚠ {unconfiguredDevices.length} Gerät(e) sind noch nicht vollständig konfiguriert
                    </div>

                    <button
                        onClick={() => setEditingDevice(null)}  // plus mode="bulk"
                        className="bg-yellow-500 hover:bg-yellow-600 text-white text-sm px-3 py-1 rounded"
                    >
                        Jetzt konfigurieren
                    </button>

                </div>
            )}

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
                <DeviceSetupModal
                    open={!!editingDevice}
                    onClose={() => setEditingDevice(null)}
                    mode="single"
                    singleDevice={editingDevice}
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
