/*
# src/components/device/TrashBinModal.jsx
*/

import { useState, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "../../api/client";

export default function TrashBinModal({
    open,
    onClose,
}) {

    const queryClient = useQueryClient();

    const [selectedIds, setSelectedIds] = useState([]);

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

    const trashQuery = useQuery({
        queryKey: ["device-trash"],
        queryFn: () => apiFetch("/api/devices/trash/"),
        enabled: open,
    });

    if (!open) {
        return null;
    }

    const devices = trashQuery.data ?? [];

    const allSelected =
        devices.length > 0 &&
        devices.every(d => selectedIds.includes(d.id));

    function toggleDevice(id) {

        setSelectedIds(prev =>
            prev.includes(id)
                ? prev.filter(x => x !== id)
                : [...prev, id]
        );
    }

    function toggleAll() {

        if (allSelected) {
            setSelectedIds([]);
            return;
        }

        setSelectedIds(
            devices.map(d => d.id)
        );
    }

    async function restoreSelected() {

        if (!selectedIds.length) {
            return;
        }

        try {

            await apiFetch("/api/devices/restore/", {
                method: "POST",
                body: JSON.stringify({
                    device_ids: selectedIds,
                }),
            });

            await Promise.all([
                queryClient.invalidateQueries({
                    queryKey: ["devices"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["device-trash"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["unconfigured-devices"],
                }),
            ]);

            setSelectedIds([]);

        } catch (err) {

            console.error(err);
            alert("Wiederherstellen fehlgeschlagen.");
        }
    }

    async function purgeSelected() {

        if (!selectedIds.length) {
            return;
        }

        const confirmed = window.confirm(
            "Ausgewählte Geräte endgültig löschen?"
        );

        if (!confirmed) {
            return;
        }

        try {

            await apiFetch("/api/devices/purge/", {
                method: "POST",
                body: JSON.stringify({
                    device_ids: selectedIds,
                }),
            });

            await Promise.all([
                queryClient.invalidateQueries({
                    queryKey: ["devices"],
                }),
                queryClient.invalidateQueries({
                    queryKey: ["device-trash"],
                }),
            ]);

            setSelectedIds([]);

        } catch (err) {

            console.error(err);
            alert("Löschen fehlgeschlagen.");
        }
    }

    return (
        <div
            className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center"
            onClick={onClose}
        >
            <div
                className="
                bg-white
                rounded-xl
                shadow-xl
                w-full
                max-w-2xl
                h-[80vh]
                flex
                flex-col
            "
                onClick={(e) => e.stopPropagation()}
            >

                {/* Header */}

                <div className="p-4 border-b bg-gradient-to-r from-amber-50 to-orange-50">

                    <div className="flex justify-between items-center">

                        <div className="flex items-center gap-3">

                            <div className="w-10 h-10 rounded-xl bg-amber-100 flex items-center justify-center text-xl shadow-sm">
                                ♻️
                            </div>

                            <div>

                                <h2 className="font-semibold text-lg text-gray-900">
                                    Papierkorb
                                </h2>

                                <div className="text-xs text-gray-500">
                                    Entfernte Geräte verwalten
                                </div>

                            </div>

                        </div>

                        <div className="flex items-center gap-3">

                            <div
                                title="Geräte bleiben 7 Tage im Papierkorb. Wenn Home Assistant, ioBroker oder MQTT weiterhin Daten senden, kann ein Gerät nach der endgültigen Löschung automatisch erneut erkannt werden."
                                className="
                                w-8 h-8
                                rounded-full
                                bg-amber-100
                                text-amber-700
                                flex items-center justify-center
                                cursor-help
                                text-sm
                                font-medium
                            "
                            >
                                ℹ
                            </div>

                            <button
                                onClick={onClose}
                                className="text-gray-400 hover:text-gray-600 text-lg"
                            >
                                ✕
                            </button>

                        </div>

                    </div>

                </div>

                {/* Content */}

                <div className="flex-1 overflow-y-auto p-4">

                    {trashQuery.isLoading ? (

                        <div>Lade Papierkorb...</div>

                    ) : (

                        <>

                            <label className="flex items-center gap-2 mb-4">

                                <input
                                    type="checkbox"
                                    checked={allSelected}
                                    onChange={toggleAll}
                                />

                                Alle auswählen

                            </label>

                            <div className="space-y-2">

                                {devices.length === 0 && (
                                    <div className="p-6 text-center text-gray-500 border rounded-xl">
                                        Papierkorb ist leer
                                    </div>
                                )}

                                {devices.map(device => (

                                    <div
                                        key={device.id}
                                        className="
                                        border rounded-xl
                                        p-3
                                        bg-white
                                        shadow-sm
                                        hover:shadow-md
                                        transition-all
                                    "
                                    >

                                        <div className="flex items-start gap-3">

                                            <input
                                                type="checkbox"
                                                checked={selectedIds.includes(device.id)}
                                                onChange={() => toggleDevice(device.id)}
                                                className="mt-1"
                                            />

                                            <div className="flex-1">

                                                <div className="flex items-start justify-between">

                                                    <div>

                                                        <div className="font-medium text-gray-900">
                                                            {device.display_name}
                                                        </div>

                                                        <div className="text-xs text-gray-500">
                                                            {device.identifier}
                                                        </div>

                                                    </div>

                                                    <div className="px-2 py-1 text-xs rounded-full bg-amber-100 text-amber-700">
                                                        ♻ Vorgemerkt
                                                    </div>

                                                </div>

                                                <div className="mt-2 space-y-1 text-sm">

                                                    <div className="flex items-center gap-2 text-gray-600">
                                                        <span>🕒</span>
                                                        <span>
                                                            {device.last_seen
                                                                ? new Date(device.last_seen).toLocaleString("de-DE")
                                                                : "Keine Aktivität bekannt"}
                                                        </span>
                                                    </div>

                                                    <div className="flex items-center gap-2 text-orange-700">
                                                        <span>🗑️</span>
                                                        <span>
                                                            {device.delete_after
                                                                ? `Löschung geplant am ${new Date(device.delete_after).toLocaleString("de-DE")}`
                                                                : "Kein Löschdatum"}
                                                        </span>
                                                    </div>

                                                </div>

                                            </div>

                                        </div>

                                    </div>

                                ))}

                            </div>

                        </>

                    )}

                </div>

                {/* Footer */}

                <div className="border-t p-4 flex justify-between items-center bg-gray-50">

                    <div className="text-sm text-gray-500">
                        {selectedIds.length} ausgewählt
                    </div>

                    <div className="flex gap-2">

                        <button
                            onClick={restoreSelected}
                            disabled={!selectedIds.length}
                            className="
                            px-4 py-2 rounded-lg
                            bg-emerald-600 hover:bg-emerald-700
                            text-white
                            disabled:bg-gray-300
                        "
                        >
                            Wiederherstellen
                        </button>

                        <button
                            onClick={purgeSelected}
                            disabled={!selectedIds.length}
                            className="
                            px-4 py-2 rounded-lg
                            bg-red-600 hover:bg-red-700
                            text-white
                            disabled:bg-gray-300
                        "
                        >
                            Endgültig löschen
                        </button>

                    </div>

                </div>

            </div>

        </div>
    )
}