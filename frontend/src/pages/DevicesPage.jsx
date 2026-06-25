/*
# src/pages/DevicesPage.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";


/* =========================================================
   DEVICE CARD
========================================================= */
function DeviceCard({ device }) {

    const config = device.config || {};
    const isOnline = device.status === "online";

    function getIcon(roleKey) {
        switch (roleKey) {
            case "producer": return "⚡";
            case "consumer": return "🔌";
            case "battery": return "🔋";
            default: return "📦";
        }
    }

    return (
        <div className="border rounded-xl p-4 shadow-sm bg-white hover:shadow-md transition">

            {/* HEADER */}
            <div className="flex justify-between mb-2">

                <div>
                    <div className="font-semibold flex items-center gap-2">
                        <span>{getIcon(config.role?.key)}</span>
                        {device.display_name}
                    </div>

                    <div className="text-xs text-gray-400">
                        {device.identifier}
                    </div>
                </div>

                {/* STATUS DOT */}
                <div
                    className={`w-3 h-3 rounded-full mt-1 ${isOnline ? "bg-green-500" : "bg-gray-300"
                        }`}
                />
            </div>

            {/* ROLE */}
            <div className="text-sm text-gray-500 mb-2">
                {config.role?.label || "–"}
            </div>

            {/* VALUE */}
            <div className="text-xl font-bold text-indigo-600">
                {device.value != null
                    ? `${device.value} ${device.unit || ""}`
                    : "--"}
            </div>

        </div>
    );
}


/* =========================================================
   DASHBOARD PAGE
========================================================= */
export default function DashboardPage() {

    // ✅ Geräte
    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
    });

    // ✅ Status (LIVE)
    const statusQuery = useQuery({
        queryKey: ["devices-status"],
        queryFn: () => apiFetch("/api/devices/status/"),
        refetchInterval: 5000,
    });

    // ✅ Werte (optional – falls vorhanden)
    const valuesQuery = useQuery({
        queryKey: ["devices-values"],
        queryFn: () => apiFetch("/api/devices/latest/"),
        refetchInterval: 3000,
        retry: false, // endpoint evtl. noch nicht da
    });

    const devices = devicesQuery.data || [];
    const statusList = statusQuery.data || [];
    const values = valuesQuery.data || [];

    // ✅ MERGE STATUS + VALUES
    const merged = devices.map(d => {

        const status = statusList.find(s => s.id === d.id);
        const value = values.find(v => v.device === d.id);

        return {
            ...d,
            status: status?.status || "offline",
            last_seen: status?.last_seen,
            value: value?.value,
            unit: value?.unit,
        };
    });

    // ✅ GRUPPIERUNG NACH RAUM
    const grouped = merged.reduce((acc, d) => {
        const room = d.config?.room?.name || "Ohne Raum";
        acc[room] = acc[room] || [];
        acc[room].push(d);
        return acc;
    }, {});

    return (
        <div className="p-6 max-w-6xl">

            <h1 className="text-2xl font-semibold mb-6">
                Dashboard
            </h1>

            {devices.length === 0 && (
                <div className="text-gray-500">
                    Keine Geräte vorhanden
                </div>
            )}

            {Object.entries(grouped).map(([room, devices]) => (
                <div key={room} className="mb-8">

                    {/* ROOM HEADER */}
                    <h2 className="text-sm text-gray-500 mb-3">
                        {room}
                    </h2>

                    {/* GRID */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                        {devices.map(d => (
                            <DeviceCard key={d.id} device={d} />
                        ))}
                    </div>

                </div>
            ))}

        </div>
    );
}
