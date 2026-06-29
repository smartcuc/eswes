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
                cursor-pointer border rounded-xl p-4 shadow-sm transition hover:shadow-md
                hover:ring-2 hover:ring-indigo-200
                ${missing ? "border-yellow-300 bg-yellow-50" : "border-gray-200 bg-white"}
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

                <div className="flex items-center gap-2">
                    <button
                        onClick={(e) => {
                            e.stopPropagation();
                            onEdit(device);
                        }}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        ⚙️
                    </button>

                    <div className={`w-3 h-3 rounded-full ${isOnline ? "bg-green-500" : "bg-gray-300"}`} />
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

    const [filterText, setFilterText] = useState("");
    const [statusFilter, setStatusFilter] = useState("all");

    // ✅ STRUCTURE TOGGLES
    const [showFloors, setShowFloors] = useState(true);
    const [showRooms, setShowRooms] = useState(true);

    // ✅ ROLES (multi select)
    const [activeRoles, setActiveRoles] = useState([
        "producer",
        "consumer",
        "battery"
    ]);

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

    const statusMap = Object.fromEntries((statusQuery.data || []).map(s => [s.id, s]));
    const valueMap = Object.fromEntries((valuesQuery.data || []).map(v => [v.device, v]));

    const merged = useMemo(() => {
        return devices.map(d => ({
            ...d,
            status: (statusMap[d.id]?.status || "offline").toLowerCase(),
            value: valueMap[d.id]?.value,
            unit: valueMap[d.id]?.unit,
        }));
    }, [devices, statusMap, valueMap]);

    const roleLabels = {
        producer: "⚡ Erzeuger",
        consumer: "🔌 Verbraucher",
        battery: "🔋 Speicher"
    };

    const roleStats = useMemo(() => {
        const map = {};
        merged.forEach(d => {
            const key = d.config?.role?.key;
            if (!key) return;
            map[key] = (map[key] || 0) + 1;
        });
        return map;
    }, [merged]);

    /* ✅ FILTER */

    const filtered = useMemo(() => {

        let list = [...merged];

        if (filterText) {
            const t = filterText.trim().toLowerCase();
            list = list.filter(d =>
                (d.display_name || "").toLowerCase().includes(t) ||
                (d.identifier || "").toLowerCase().includes(t)
            );
        }

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

        list = list.filter(d => {
            const role = d.config?.role?.key;
            return role ? activeRoles.includes(role) : true;
        });

        return list;

    }, [merged, filterText, statusFilter, activeRoles]);

    /* ✅ BANNER */

    const unconfiguredDevices = useMemo(() => {
        return filtered.filter(d => {
            const c = d.config || {};
            return !c.role || !c.measurement_type;
        });
    }, [filtered]);

    /* ✅ GROUPING */

    const grouped = useMemo(() => {

        return filtered.reduce((acc, d) => {

            const floor = showFloors
                ? (d.config?.floor?.name || "Ohne Etage")
                : "Alle Geräte";

            const room = showRooms
                ? (d.config?.room?.name || "Ohne Raum")
                : "__ALL__";

            acc[floor] = acc[floor] || {};
            acc[floor][room] = acc[floor][room] || [];
            acc[floor][room].push(d);

            return acc;

        }, {});

    }, [filtered, showFloors, showRooms]);

    if (devicesQuery.isLoading) {
        return <div className="p-6">Lade Geräte…</div>;
    }

    return (
        <div className="p-6 max-w-6xl">

            {/* FILTER BAR */}
            <div className="flex flex-wrap gap-3 mb-6">

                <input
                    placeholder="Gerät suchen…"
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    className="border px-3 py-2 rounded w-52"
                />

                {/* STATUS */}
                {["all", "online", "offline", "missing"].map(k => (
                    <button
                        key={k}
                        onClick={() => setStatusFilter(prev => prev === k ? "all" : k)}
                        className={`px-3 py-1 rounded-full text-sm border ${statusFilter === k ? "bg-indigo-600 text-white" : "bg-white"
                            }`}
                    >
                        {k}
                    </button>
                ))}

                {/* ROLE CHIPS */}
                {["producer", "consumer", "battery"].map(role => {

                    const active = activeRoles.includes(role);

                    return (
                        <button
                            key={role}
                            onClick={() => {
                                setActiveRoles(prev =>
                                    prev.includes(role)
                                        ? prev.filter(r => r !== role)
                                        : [...prev, role]
                                );
                            }}
                            className={`px-3 py-1 rounded-full text-sm border ${active ? "bg-indigo-600 text-white" : "bg-white"
                                }`}
                        >
                            {roleLabels[role]} ({roleStats[role] || 0})
                        </button>
                    );
                })}

                {/* STRUCTURE TOGGLES */}
                <label className="flex items-center gap-1 text-sm">
                    <input
                        type="checkbox"
                        checked={showFloors}
                        onChange={(e) => setShowFloors(e.target.checked)}
                    />
                    Etagen
                </label>

                <label className="flex items-center gap-1 text-sm">
                    <input
                        type="checkbox"
                        checked={showRooms}
                        onChange={(e) => setShowRooms(e.target.checked)}
                    />
                    Räume
                </label>

            </div>

            {/* BANNER */}
            {unconfiguredDevices.length > 0 && (
                <div
                    onClick={() => {
                        setModalMode("bulk");
                        setEditingDevice(null);
                    }}
                    className="mb-6 p-4 rounded-lg border border-yellow-300 bg-yellow-50 flex items-center justify-between cursor-pointer hover:bg-yellow-100"
                >
                    <div className="text-yellow-800 text-sm">
                        ⚠ {unconfiguredDevices.length} Gerät(e) nicht vollständig konfiguriert
                    </div>

                    <span className="text-sm text-white bg-yellow-500 px-3 py-1 rounded">
                        Jetzt konfigurieren
                    </span>
                </div>
            )}

            {/* GRID */}
            {Object.entries(grouped).map(([floor, rooms]) => (
                <div key={floor} className="mb-6">

                    {showFloors && (
                        <h2 className="text-sm text-gray-500 mb-2">{floor}</h2>
                    )}

                    {Object.entries(rooms).map(([room, devices]) => (
                        <div key={room} className="mb-4">

                            {showRooms && room !== "__ALL__" && (
                                <h3 className="text-xs text-gray-400 mb-2">{room}</h3>
                            )}

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
