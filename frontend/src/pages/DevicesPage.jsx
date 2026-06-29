/*
# src/pages/DevicesPage.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { apiFetch } from "../api/client";
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
            default: return "🔧";
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
                            className={`w-3 h-3 rounded-full ${isOnline ? "bg-green-500" : "bg-gray-300"}`}
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
                    : <span className="text-gray-400">keine Daten</span>
                }
            </div>

            {missing && (
                <div className="text-xs text-yellow-700 mt-2">
                    ⚠ Unvollständig konfiguriert
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
    const [modalMode, setModalMode] = useState(null);
    const [editingDevice, setEditingDevice] = useState(null);

    /* ✅ FILTER STATE */
    const [filterText, setFilterText] = useState("");
    const [statusFilter, setStatusFilter] = useState("all"); // chips
    const [sortKey, setSortKey] = useState("name");
    const [selectedHome, setSelectedHome] = useState("all");

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

    // ✅ HOMES (Level 3)
    const homesQuery = useQuery({
        queryKey: ["homes"],
        queryFn: () => apiFetch("/api/devices/homes/"),
    });

    const homes = homesQuery.data || [];
    const hasMultipleHomes = homes.length > 1;

    /* ✅ DATA PREP */

    const devices = useMemo(() => {
        return (devicesQuery.data || [])
            .slice()
            .sort((a, b) =>
                (a.display_name || "").localeCompare(b.display_name || "")
            );
    }, [devicesQuery.data]);

    const statusList = statusQuery.data || [];
    const values = valuesQuery.data || [];

    const statusMap = useMemo(
        () => Object.fromEntries(statusList.map(s => [s.id, s])),
        [statusList]
    );

    const valueMap = useMemo(
        () => Object.fromEntries(values.map(v => [v.device, v])),
        [values]
    );

    const merged = useMemo(() => {
        return devices.map(d => ({
            ...d,
            status: statusMap[d.id]?.status || "offline",
            value: valueMap[d.id]?.value,
            unit: valueMap[d.id]?.unit,
        }));
    }, [devices, statusMap, valueMap]);

    /* ✅ FILTER + SORT */

    const filtered = useMemo(() => {

        let list = [...merged];

        // 🔍 SEARCH
        if (filterText) {
            const t = filterText.toLowerCase();
            list = list.filter(d =>
                (d.display_name || "").toLowerCase().includes(t) ||
                (d.identifier || "").toLowerCase().includes(t)
            );
        }

        // 🟢 STATUS CHIP FILTER
        if (statusFilter === "online") {
            list = list.filter(d => d.status === "online");
        }

        if (statusFilter === "offline") {
            list = list.filter(d => d.status !== "online");
        }

        if (statusFilter === "missing") {
            list = list.filter(d => {
                const c = d.config || {};
                return !c.role || !c.measurement_type;
            });
        }

        // 🏠 MULTI HOME
        if (selectedHome !== "all") {
            list = list.filter(d => d.config?.home?.id === Number(selectedHome));
        }

        // 🔄 SORT
        list.sort((a, b) => {

            if (sortKey === "value") {
                return (b.value ?? 0) - (a.value ?? 0);
            }

            if (sortKey === "status") {
                return a.status.localeCompare(b.status);
            }

            return (a.display_name || "")
                .localeCompare(b.display_name || "");
        });

        return list;

    }, [merged, filterText, statusFilter, sortKey, selectedHome]);

    const grouped = useMemo(() => {
        return filtered
            .slice()
            .sort((a, b) => {
                const roomA = a.config?.room?.name || "";
                const roomB = b.config?.room?.name || "";

                if (roomA !== roomB) return roomA.localeCompare(roomB);

                return (a.display_name || "")
                    .localeCompare(b.display_name || "");
            })
            .reduce((acc, d) => {
                const room = d.config?.room?.name || "Ohne Raum";
                acc[room] = acc[room] || [];
                acc[room].push(d);
                return acc;
            }, {});
    }, [filtered]);

    /* ✅ RETURNS */

    if (devicesQuery.isLoading) {
        return (
            <div className="p-6 text-gray-400 animate-pulse">
                Lade Geräte...
            </div>
        );
    }

    if (!devices.length) {
        return (
            <div className="p-6 text-gray-500">
                Noch keine Geräte vorhanden.
            </div>
        );
    }

    return (
        <div className="p-6 max-w-6xl">

            <h1 className="text-2xl font-semibold mb-6">
                Geräte
            </h1>

            {/* ✅ LEVEL 3 FILTER BAR */}
            <div className="flex flex-wrap gap-3 mb-6 items-center">

                {/* SEARCH */}
                <input
                    placeholder="Gerät suchen…"
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    className="border px-3 py-2 rounded w-52"
                />

                {/* FILTER CHIPS */}
                <div className="flex gap-2">

                    {["all", "online", "offline", "missing"].map(key => {

                        const active = statusFilter === key;

                        const labels = {
                            all: "Alle",
                            online: "Online",
                            offline: "Offline",
                            missing: "Unvollständig"
                        };

                        return (
                            <button
                                key={key}
                                onClick={() => setStatusFilter(key)}
                                className={`
                                    px-3 py-1 rounded-full text-sm border
                                    ${active
                                        ? "bg-indigo-600 text-white border-indigo-600"
                                        : "bg-white text-gray-600 border-gray-300 hover:bg-gray-100"}
                                `}
                            >
                                {labels[key]}
                            </button>
                        );
                    })}

                </div>

                {/* SORT */}
                <select
                    value={sortKey}
                    onChange={(e) => setSortKey(e.target.value)}
                    className="border px-3 py-2 rounded"
                >
                    <option value="name">Name</option>
                    <option value="value">Wert</option>
                    <option value="status">Status</option>
                </select>

                {/* MULTI HOME */}
                {hasMultipleHomes && (
                    <select
                        value={selectedHome}
                        onChange={(e) => setSelectedHome(e.target.value)}
                        className="border px-3 py-2 rounded"
                    >
                        <option value="all">Alle Homes</option>
                        {homes.map(h => (
                            <option key={h.id} value={h.id}>
                                {h.name}
                            </option>
                        ))}
                    </select>
                )}

            </div>

            {/* GRID */}
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
                                    onEdit={(dev) => {
                                        setEditingDevice(dev);
                                        setModalMode("single");
                                    }}
                                />
                            ))}
                        </div>

                    </div>
                ))}

            <DeviceSetupModal
                open={!!modalMode}
                onClose={() => {
                    setModalMode(null);
                    setEditingDevice(null);
                }}
                mode={modalMode || "bulk"}
                singleDevice={editingDevice}
            />

            {chartDevice && (
                <DeviceChartModal
                    device={chartDevice}
                    onClose={() => setChartDevice(null)}
                />
            )}

        </div>
    );
}
