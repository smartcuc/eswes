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


    const devices = (isBulk
        ? bulkDevices
        : singleDevice ? [singleDevice] : []
    ).slice().sort((a, b) =>
        (a.display_name || "").localeCompare(b.display_name || "")
    );

    const [index, setIndex] = useState(0);

    const device = isBulk
        ? devices[index]
        : singleDevice;

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
    const autoTimer = useRef(null);

    /* RESET */
    useEffect(() => {
        if (open) {
            setIndex(0);
            setLocalValues({});
            setSaving({});
            setSaved({});
            setError({});
            setServerDevices({});
        }
    }, [open]);

    /* ESC */
    useEffect(() => {

        if (!open) {
            return;
        }

        function handleKeyDown(event) {

            if (event.key === "Escape") {
                onClose();
            }
        }

        window.addEventListener("keydown", handleKeyDown);

        return () => {
            window.removeEventListener("keydown", handleKeyDown);
        };

    }, [open, onClose]);

    /* SAVE */
    async function saveDevice(id, values) {
        console.log("SAVE VALUES", values);
        if (!values || Object.keys(values).length === 0) return;

        const key = String(id);

        setSaving(prev => ({ ...prev, [key]: true }));
        setError(prev => ({ ...prev, [key]: false }));

        let baseDevice =
            serverDevices[key] ||
            devices.find(d => d.id === id);

        // 🔥 Fallback NUR wenn gar nichts da ist
        if (!baseDevice && singleDevice) {
            baseDevice = singleDevice;
        }

        const server = baseDevice;

        try {

            const payload = {
                display_name: values.display_name ?? server.display_name ?? "",
                role_id: values.role_id ?? server.config?.role?.id ?? null,
                measurement_type: values.measurement_type ?? server.config?.measurement_type ?? null,
                room_id: values.room_id ?? server.config?.room?.id ?? null,
                floor_id: values.floor_id ?? server.config?.floor?.id ?? null,
                home_id: values.home_id ?? server.config?.home?.id ?? null,
                energy_source: values.energy_source ?? server.config?.energy_source ?? "",
                energy_group: values.energy_group ?? server.config?.energy_group ?? "",

            }
            // ✅ FIX: Home aus room/floor ableiten, wenn es fehlt
            if (!payload.home_id) {

                let floorIdToCheck = payload.floor_id;

                // ✅ wenn room gesetzt → zuerst floor daraus bestimmen
                if (payload.room_id) {
                    const room = rooms.find(r => r.id === payload.room_id);
                    if (room?.floor?.id) {
                        floorIdToCheck = room.floor.id;
                    }
                }

                // ✅ dann home aus floor holen
                if (floorIdToCheck) {
                    const floor = floors.find(f => f.id === floorIdToCheck);
                    if (floor?.home?.id) {
                        payload.home_id = floor.home.id;
                    }
                }
            }

            const data = await apiFetch(`/api/devices/${id}/`, {
                method: "PATCH",
                body: JSON.stringify(payload)
            });

            if (data?.device) {
                setServerDevices(prev => ({
                    ...prev,
                    [data.device.id]: data.device
                }));

                setLocalValues(prev => {
                    const copy = { ...prev };
                    delete copy[key];
                    return copy;
                });
            }

            setSaving(prev => ({ ...prev, [key]: false }));
            setSaved(prev => ({ ...prev, [key]: true }));

            setTimeout(() => {
                setSaved(prev => ({ ...prev, [key]: false }));
            }, 1000);

            if (query?.refetch) query.refetch();

        } catch (err) {

            console.error("save failed", err);

            setSaving(prev => ({ ...prev, [key]: false }));
            setError(prev => ({ ...prev, [key]: true }));
        }

        // ✅ AUTO ADVANCE (unverändert korrekt)
        if (
            values.role_id &&
            values.measurement_type &&
            index < devices.length - 1
        ) {
            if (autoTimer.current) clearTimeout(autoTimer.current);

            autoTimer.current = setTimeout(() => {
                setIndex(i => i + 1);
            }, 800);
        }
    }

    function handleChange(id, field, value) {
        const key = String(id);
        console.log("CHANGE", field, value);
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

    if (!open || !device) return null;

    const key = String(device.id);
    const local = localValues[key] || {};
    const server = serverDevices[key] || device;

    const displayName = local.display_name ?? server.display_name ?? "";
    const roleId = local.role_id ?? server.config?.role?.id ?? "";
    const measurementType = local.measurement_type ?? server.config?.measurement_type ?? "";
    const homeId = local.home_id ?? server.config?.home?.id ?? "";
    const floorId = local.floor_id ?? server.config?.floor?.id ?? "";
    const roomId = local.room_id ?? server.config?.room?.id ?? "";

    const energySource = local.energy_source ?? server.config?.energy_source ?? "";
    const energyGroup = local.energy_group ?? server.config?.energy_group ?? "";

    const progress = ((index + 1) / devices.length) * 100;

    return (
        <div
            className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center"
            onClick={onClose}
        >
            <div
                className="
                    bg-white
                    rounded-2xl
                    shadow-xl
                    w-full
                    max-w-2xl
                    h-[80vh]
                    flex
                    flex-col
                    overflow-hidden
                "
                onClick={(e) => e.stopPropagation()}
            >

                {/* HEADER */}

                <div className="p-4 border-b bg-gradient-to-r from-indigo-50 to-blue-50">

                    <div className="flex justify-between items-start">

                        <div>

                            <div className="text-xs text-gray-500">
                                Gerät {index + 1} von {devices.length}
                            </div>

                            <h2 className="text-lg font-semibold text-gray-900">
                                ⚙️ Gerät einrichten
                            </h2>

                            <div className="text-sm text-gray-500">
                                Funktion, Messdaten und Position festlegen
                            </div>

                        </div>

                        <button
                            onClick={onClose}
                            className="text-gray-400 hover:text-gray-600 text-lg"
                        >
                            ✕
                        </button>

                    </div>

                    <div className="w-full bg-gray-200 h-2 rounded mt-4">

                        <div
                            className="bg-indigo-600 h-2 rounded"
                            style={{ width: `${progress}%` }}
                        />

                    </div>

                </div>

                {/* CONTENT */}

                <div className="flex-1 overflow-y-auto">

                    <div className="max-w-xl mx-auto p-6 space-y-4">

                        {/* NAME */}

                        <div>

                            <label className="text-xs text-gray-400">
                                Name
                            </label>

                            <input
                                value={displayName}
                                onChange={(e) =>
                                    handleChange(
                                        device.id,
                                        "display_name",
                                        e.target.value
                                    )
                                }
                                className="border px-3 py-2 w-full rounded"
                            />

                            <p className="text-xs text-gray-400 mt-1">
                                Anzeige im Dashboard
                            </p>

                        </div>

                        {/* ROLE */}

                        <div>

                            <label className="text-xs text-gray-400">
                                Funktion des Geräts *
                            </label>

                            <select
                                value={roleId}
                                onChange={(e) =>
                                    handleChange(
                                        device.id,
                                        "role_id",
                                        e.target.value
                                            ? Number(e.target.value)
                                            : null
                                    )
                                }
                                className={`border px-3 py-2 w-full rounded ${!roleId
                                    ? "border-red-300 bg-red-50"
                                    : ""
                                    }`}
                            >
                                <option value="">
                                    Bitte wählen
                                </option>

                                {roles.map(r => (
                                    <option
                                        key={r.id}
                                        value={r.id}
                                    >
                                        {r.label}
                                    </option>
                                ))}
                            </select>

                            <p className="text-xs text-gray-400 mt-1">
                                Erzeuger, Verbraucher oder Speicher
                            </p>

                        </div>

                        {/* MEASUREMENT */}

                        <div>

                            <label className="text-xs text-gray-400">
                                Messdaten *
                            </label>

                            <select
                                value={measurementType}
                                onChange={(e) =>
                                    handleChange(
                                        device.id,
                                        "measurement_type",
                                        e.target.value || null
                                    )
                                }
                                className={`border px-3 py-2 w-full rounded ${!measurementType
                                    ? "border-red-300 bg-red-50"
                                    : ""
                                    }`}
                            >
                                <option value="">
                                    Bitte wählen
                                </option>

                                {measurementTypes.map(m => (
                                    <option
                                        key={m.key || m.id}
                                        value={m.key || m.value}
                                    >
                                        {m.label || m.name}
                                    </option>
                                ))}
                            </select>

                            <p className="text-xs text-gray-400 mt-1">
                                Welche Werte liefert dieses Gerät?
                            </p>

                        </div>

                        <div>

                            <label className="text-xs text-gray-400">
                                Energiequelle
                            </label>

                            <select
                                value={energySource}
                                onChange={(e) =>
                                    handleChange(
                                        device.id,
                                        "energy_source",
                                        e.target.value
                                    )
                                }
                                className="border px-3 py-2 w-full rounded"
                            >
                                <option value="">Bitte wählen</option>

                                <option value="grid">Netz</option>
                                <option value="pv">PV</option>
                                <option value="battery">Batterie</option>
                                <option value="heatpump">Wärmepumpe</option>
                                <option value="ev">Wallbox</option>
                                <option value="household">Haushalt</option>
                                <option value="other">Sonstige</option>
                            </select>

                        </div>

                        <div>

                            <label className="text-xs text-gray-400">
                                Energiegruppe
                            </label>

                            <select
                                value={energyGroup}
                                onChange={(e) =>
                                    handleChange(
                                        device.id,
                                        "energy_group",
                                        e.target.value
                                    )
                                }
                                className="border px-3 py-2 w-full rounded"
                            >
                                <option value="">Bitte wählen</option>

                                <option value="grid">Netz</option>
                                <option value="generation">Erzeugung</option>
                                <option value="storage">Speicher</option>
                                <option value="heating">Heizung</option>
                                <option value="mobility">Mobilität</option>
                                <option value="household">Haushalt</option>
                                <option value="other">Sonstige</option>
                            </select>

                        </div>

                        {/* LOCATION */}

                        <div>

                            <label className="text-xs text-gray-400">
                                Position (optional)
                            </label>

                            <div className="grid grid-cols-2 gap-3 mt-2">

                                {hasMultipleHomes && (

                                    <select
                                        value={homeId}
                                        onChange={(e) =>
                                            handleChange(
                                                device.id,
                                                "home_id",
                                                e.target.value
                                                    ? Number(e.target.value)
                                                    : null
                                            )
                                        }
                                        className="border px-2 py-2 rounded"
                                    >
                                        <option value="">
                                            🏠 Zuhause
                                        </option>

                                        {homes.map(h => (
                                            <option
                                                key={h.id}
                                                value={h.id}
                                            >
                                                {h.name}
                                            </option>
                                        ))}

                                    </select>

                                )}

                                <select
                                    value={floorId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "floor_id",
                                            e.target.value
                                                ? Number(e.target.value)
                                                : null
                                        )
                                    }
                                    className="border px-2 py-2 rounded"
                                >
                                    <option value="">
                                        🏢 Etage
                                    </option>

                                    {floors.map(f => (
                                        <option
                                            key={f.id}
                                            value={f.id}
                                        >
                                            {f.name}
                                        </option>
                                    ))}
                                </select>

                                <select
                                    value={roomId}
                                    onChange={(e) =>
                                        handleChange(
                                            device.id,
                                            "room_id",
                                            e.target.value
                                                ? Number(e.target.value)
                                                : null
                                        )
                                    }
                                    className="border px-2 py-2 rounded"
                                >
                                    <option value="">
                                        🚪 Raum
                                    </option>

                                    {rooms.map(r => (
                                        <option
                                            key={r.id}
                                            value={r.id}
                                        >
                                            {r.name}
                                        </option>
                                    ))}
                                </select>

                            </div>

                            <p className="text-xs text-gray-400 mt-1">
                                Hilft bei Auswertung und Visualisierung
                                (z. B. Sankey)
                            </p>

                        </div>

                    </div>

                </div>

                {/* FOOTER */}

                <div className="border-t p-4 flex justify-between items-center bg-gray-50">

                    <div className="text-sm">

                        {saving[key] && (
                            <span>
                                ⏳ Speichern...
                            </span>
                        )}

                        {saved[key] && (
                            <span className="text-green-600">
                                ✅ Gespeichert
                            </span>
                        )}

                        {error[key] && (
                            <span className="text-red-600">
                                ❌ Fehler
                            </span>
                        )}

                    </div>

                    <div className="flex gap-2">

                        {devices.length > 1 && (

                            <button
                                onClick={() =>
                                    setIndex(i =>
                                        Math.max(0, i - 1)
                                    )
                                }
                                disabled={index === 0}
                                className="
                    px-4 py-2
                    border
                    rounded-lg
                    disabled:opacity-30
                "
                            >
                                ← Zurück
                            </button>

                        )}

                        <button
                            onClick={() => {

                                if (
                                    devices.length <= 1 ||
                                    index === devices.length - 1
                                ) {
                                    onClose();
                                } else {
                                    setIndex(i => i + 1);
                                }

                            }}
                            className="
                px-4 py-2
                rounded-lg
                bg-indigo-600
                hover:bg-indigo-700
                text-white
            "
                        >
                            {devices.length <= 1 ||
                                index === devices.length - 1
                                ? "Fertig"
                                : "Weiter →"}
                        </button>

                    </div>

                </div>


            </div>

        </div>
    );
}