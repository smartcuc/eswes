/*
# src/pages/DevicesPage.jsx
*/

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useMemo, useEffect } from "react";
import { apiFetch } from "../api/client";
import DeviceChartModal from "../components/device/DeviceChartModal";
import DeviceSetupModal from "../components/device/DeviceSetupModal";
import useUserPreference from "../hooks/useUserPreference";


function ensureOrder(items, storedOrder) {

    const itemIds = items.map(item => item.id);

    const existing = storedOrder.filter(id =>
        itemIds.includes(id)
    );

    const missing = itemIds.filter(id =>
        !existing.includes(id)
    );

    return [...existing, ...missing];
}


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
                {device.value != null ? (
                    `${device.value} ${device.unit || ""}`
                ) : device.status === "stale" ? (
                    <span className="text-gray-400">
                        Keine aktuellen Daten
                    </span>
                ) : device.status === "offline" ? (
                    <span className="text-gray-400">
                        offline
                    </span>
                ) : (
                    <span className="text-gray-400">
                        Keine Daten
                    </span>
                )}
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

const statusOptions = [
    {
        key: "online",
        icon: "🟢",
        label: "Online",
        title: "Nur Geräte mit aktuellen Daten",
    },
    {
        key: "offline",
        icon: "⚫",
        label: "Offline",
        title: "Geräte ohne aktuelle Daten",
    },
    {
        key: "missing",
        icon: "⚠️",
        label: "Offen",
        title: "Unvollständig konfigurierte Geräte",
    },
];

const roleOptions = {
    producer: {
        icon: "⚡",
        label: "Erzeuger",
        title: "Energieerzeuger anzeigen",
    },
    consumer: {
        icon: "🔌",
        label: "Verbraucher",
        title: "Energieverbraucher anzeigen",
    },
    battery: {
        icon: "🔋",
        label: "Speicher",
        title: "Batteriespeicher anzeigen",
    },
};

export default function DevicesPage() {

    const queryClient = useQueryClient();

    const [chartDevice, setChartDevice] = useState(null);
    const [modalMode, setModalMode] = useState(null);
    const [editingDevice, setEditingDevice] = useState(null);

    function handleDeviceUpdated(device) {

        queryClient.setQueryData(
            ["devices"],
            old => old?.map(d =>
                d.id === device.id ? device : d
            ) || []
        );
    }

    const [filterText, setFilterText] = useState("");

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

    const {
        value: settings,
        setValue: saveSettings,
        isLoading: settingsLoading,
    } = useUserPreference("devicepage");

    const showFloors = useMemo(
        () => settings.showFloors ?? true,
        [settings.showFloors]
    );

    const showRooms = useMemo(
        () => settings.showRooms ?? true,
        [settings.showRooms]
    );

    const statusFilter = useMemo(
        () => settings.statusFilter ?? null,
        [settings.statusFilter]
    );

    const activeRoles = useMemo(
        () =>
            settings.roles ?? [
                "producer",
                "consumer",
                "battery",
            ],
        [settings.roles]
    );

    const floorOrder = useMemo(
        () => settings.floorOrder ?? [],
        [settings.floorOrder]
    );

    const roomOrder = useMemo(
        () => settings.roomOrder ?? [],
        [settings.roomOrder]
    );

    const deviceOrder = useMemo(
        () => settings.deviceOrder ?? [],
        [settings.deviceOrder]
    );

    const devices = useMemo(
        () => devicesQuery.data ?? [],
        [devicesQuery.data]
    );

    const statusMap = Object.fromEntries(
        (statusQuery.data || []).map(s => [s.id, s])
    );

    const valueMap = Object.fromEntries(
        (valuesQuery.data || []).map(v => [v.device, v])
    );

    const merged = useMemo(() => {
        return devices.map(d => ({
            ...d,
            status: (statusMap[d.id]?.status || "offline").toLowerCase(),
            value: valueMap[d.id]?.value,
            unit: valueMap[d.id]?.unit,
        }));
    }, [devices, statusMap, valueMap]);


    const roleStats = useMemo(() => {
        const map = {};

        merged.forEach(d => {
            const key = d.config?.role?.key;

            if (!key) {
                return;
            }

            map[key] = (map[key] || 0) + 1;
        });

        return map;
    }, [merged]);

    const statusStats = useMemo(() => {

        return {

            online: merged.filter(
                d => d.status === "online"
            ).length,

            offline: merged.filter(
                d => d.status !== "online"
            ).length,

            missing: merged.filter(d => {

                const c = d.config || {};

                return (
                    !c.role ||
                    !c.measurement_type
                );

            }).length,

        };

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

            return role
                ? activeRoles.includes(role)
                : true;
        });

        return list;

    }, [
        merged,
        filterText,
        statusFilter,
        activeRoles,
    ]);

    /* ✅ BANNER */

    const unconfiguredDevices = useMemo(() => {

        return filtered.filter(d => {

            const c = d.config || {};

            return (
                !c.role ||
                !c.measurement_type
            );
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

    }, [
        filtered,
        showFloors,
        showRooms,
    ]);

    const allFloorIds = useMemo(() => {

        const floors = {};

        merged.forEach(d => {

            const floor = d.config?.floor;

            if (floor?.id) {
                floors[floor.id] = floor.name;
            }

        });

        return Object.entries(floors)
            .sort(([, a], [, b]) =>
                a.localeCompare(b, "de")
            )
            .map(([id]) => Number(id));

    }, [merged]);

    const allRoomIds = useMemo(() => {

        const rooms = {};

        merged.forEach(d => {

            const room = d.config?.room;

            if (room?.id) {
                rooms[room.id] = room.name;
            }

        });

        return Object.entries(rooms)
            .sort(([, a], [, b]) =>
                a.localeCompare(b, "de")
            )
            .map(([id]) => Number(id));

    }, [merged]);

    const allDeviceIds = useMemo(() => {

        return [...merged]
            .sort((a, b) =>
                (a.display_name || "").localeCompare(
                    b.display_name || "",
                    "de"
                )
            )
            .map(d => d.id);

    }, [merged]);

    useEffect(() => {

        if (!merged.length) {
            return;
        }

        const nextFloorOrder = ensureOrder(
            allFloorIds.map(id => ({ id })),
            floorOrder
        );

        const nextRoomOrder = ensureOrder(
            allRoomIds.map(id => ({ id })),
            roomOrder
        );

        const nextDeviceOrder = ensureOrder(
            allDeviceIds.map(id => ({ id })),
            deviceOrder
        );

        const changed =
            JSON.stringify(nextFloorOrder) !== JSON.stringify(floorOrder) ||
            JSON.stringify(nextRoomOrder) !== JSON.stringify(roomOrder) ||
            JSON.stringify(nextDeviceOrder) !== JSON.stringify(deviceOrder);

        if (!changed) {
            return;
        }

        saveSettings({
            ...settings,
            floorOrder: nextFloorOrder,
            roomOrder: nextRoomOrder,
            deviceOrder: nextDeviceOrder,
        });

    }, [
        merged,
        floorOrder,
        roomOrder,
        deviceOrder,
        allFloorIds,
        allRoomIds,
        allDeviceIds,
        settings,
        saveSettings,
    ]);

    if (
        devicesQuery.isLoading ||
        valuesQuery.isLoading ||
        settingsLoading
    ) {
        return <div className="p-6">Lade Geräte…</div>;
    }

    return (
        <div className="p-6 max-w-6xl">

            {/* FILTER BAR */}
            <div className="mb-3">

                <input
                    placeholder="🔍 Gerät suchen..."
                    value={filterText}
                    onChange={(e) => setFilterText(e.target.value)}
                    className="border px-3 py-2 rounded w-64"
                />

            </div>

            <div className="flex flex-wrap gap-2 mb-6">

                {/* STATUS */}
                {statusOptions.map(option => (

                    <button
                        key={option.key}
                        title={option.title}
                        onClick={() =>
                            saveSettings({
                                ...settings,
                                statusFilter:
                                    statusFilter === option.key
                                        ? null
                                        : option.key,
                            })
                        }

                        className={`
                            px-2.5 py-1
                            rounded-full
                            text-xs
                            border
                            flex items-center gap-1
                            transition
                            ${statusFilter === option.key
                                ? "bg-indigo-600 text-white border-indigo-600"
                                : "bg-white hover:bg-gray-50 border-gray-200"}
                        `}
                    >
                        <span>{option.icon}</span>
                        <span>{option.label}</span>
                        <span className="opacity-70">
                            ({statusStats[option.key] || 0})
                        </span>

                    </button>

                ))}

                {/* ROLE CHIPS */}
                {["producer", "consumer", "battery"].map(role => {

                    const active = activeRoles.includes(role);
                    const config = roleOptions[role];

                    return (
                        <button
                            key={role}
                            title={config.title}
                            onClick={() => {

                                const nextRoles =
                                    active
                                        ? activeRoles.filter(r => r !== role)
                                        : [...activeRoles, role];

                                saveSettings({
                                    ...settings,
                                    roles: nextRoles,
                                });

                            }}
                            className={`
                                px-2.5 py-1
                                rounded-full
                                text-xs
                                border
                                flex items-center gap-1
                                transition
                                ${active
                                    ? "bg-indigo-600 text-white border-indigo-600"
                                    : "bg-white hover:bg-gray-50 border-gray-200"}
                            `}
                        >
                            <span>{config.icon}</span>
                            <span>{config.label}</span>
                            <span className="opacity-70">
                                ({roleStats[role] || 0})
                            </span>
                        </button>
                    );

                })}

                {/* STRUCTURE TOGGLES */}

                <button
                    title="Geräte nach Etagen gruppieren"
                    onClick={() =>
                        saveSettings({
                            ...settings,
                            showFloors: !showFloors,
                        })
                    }
                    className={`
                        px-2.5 py-1
                        rounded-full
                        text-xs
                        border
                        flex items-center gap-1
                        transition
                        ${showFloors
                            ? "bg-indigo-600 text-white border-indigo-600"
                            : "bg-white hover:bg-gray-50 border-gray-200"}
                    `}
                >
                    🏢 Etagen
                </button>

                <button
                    title="Geräte nach Räumen gruppieren"
                    onClick={() =>
                        saveSettings({
                            ...settings,
                            showRooms: !showRooms,
                        })
                    }
                    className={`
                        px-2.5 py-1
                        rounded-full
                        text-xs
                        border
                        flex items-center gap-1
                        transition
                        ${showRooms
                            ? "bg-indigo-600 text-white border-indigo-600"
                            : "bg-white hover:bg-gray-50 border-gray-200"}
                    `}
                >
                    🚪 Räume
                </button>

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
            {Object.entries(grouped)
                .sort(([a], [b]) => a.localeCompare(b, "de"))
                .map(([floor, rooms]) => (

                    <div key={floor} className="mb-6">

                        {showFloors && (
                            <h2 className="text-sm text-gray-500 mb-2">{floor}</h2>
                        )}

                        {Object.entries(rooms)
                            .sort(([a], [b]) => a.localeCompare(b, "de"))
                            .map(([room, devices]) => (
                                <div key={room} className="mb-4">

                                    {showRooms && room !== "__ALL__" && (
                                        <h3 className="text-xs text-gray-400 mb-2">{room}</h3>
                                    )}

                                    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
                                        {[...devices]
                                            .sort((a, b) =>
                                                (a.display_name || "").localeCompare(
                                                    b.display_name || "",
                                                    "de"
                                                )
                                            )
                                            .map(d => (
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
                onDeviceUpdated={handleDeviceUpdated}
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
