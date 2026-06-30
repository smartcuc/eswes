/*
# src/components/device/TrashBinModal.jsx
*/

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "../../api/client";

export default function TrashBinModal({
    open,
    onClose,
}) {

    const queryClient = useQueryClient();

    const [selectedIds, setSelectedIds] = useState([]);

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
        <div className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center">

            <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl">

                <div className="p-4 border-b flex justify-between items-center">

                    <h2 className="font-semibold text-lg">
                        Papierkorb
                    </h2>

                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        ✕
                    </button>

                </div>

                <div className="p-4">

                    {trashQuery.isLoading ? (
                        <div>Lade Papierkorb...</div>
                    ) : (
                        <>
                            <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800">
                                Geräte werden für 7 Tage im Papierkorb aufbewahrt.

                                <div className="mt-2">
                                    Wenn ein Gerät weiterhin Daten sendet, kann es nach einer
                                    endgültigen Löschung automatisch erneut erkannt werden.
                                </div>

                                <div className="mt-2">
                                    Bitte entfernen Sie die Datenquelle (z.B. Home Assistant,
                                    ioBroker oder MQTT), bevor Sie ein Gerät endgültig löschen.
                                </div>
                            </div>

                            <label className="flex items-center gap-2 mb-4">

                                <input
                                    type="checkbox"
                                    checked={allSelected}
                                    onChange={toggleAll}
                                />

                                Alle auswählen

                            </label>

                            <div className="border rounded-lg overflow-hidden max-h-[500px] overflow-y-auto">

                                {devices.length === 0 && (
                                    <div className="p-6 text-center text-gray-500">
                                        Papierkorb ist leer
                                    </div>
                                )}

                                {devices.map(device => (

                                    <div
                                        key={device.id}
                                        className="border-b last:border-b-0 p-3 flex items-center gap-3"
                                    >

                                        <input
                                            type="checkbox"
                                            checked={selectedIds.includes(device.id)}
                                            onChange={() => toggleDevice(device.id)}
                                        />

                                        <div className="flex-1">

                                            <div className="font-medium">
                                                {device.display_name}
                                            </div>

                                            <div className="text-xs text-gray-500">
                                                {device.identifier}
                                            </div>

                                            {device.last_seen && (
                                                <div className="text-xs text-green-600 mt-1">
                                                    Zuletzt aktiv:
                                                    {" "}
                                                    {new Date(device.last_seen)
                                                        .toLocaleString("de-DE")}
                                                </div>
                                            )}

                                            {device.delete_after && (
                                                <div className="text-xs text-orange-600 mt-1">
                                                    Geplante Löschung:
                                                    {" "}
                                                    {new Date(device.delete_after)
                                                        .toLocaleDateString("de-DE")}
                                                </div>
                                            )}

                                        </div>

                                    </div>
                                ))}
                            </div>
                        </>
                    )}

                </div>

                <div className="border-t p-4 flex justify-between items-center">

                    <div className="text-sm text-gray-500">
                        {selectedIds.length} ausgewählt
                    </div>

                    <div className="flex gap-2">

                        <button
                            onClick={restoreSelected}
                            disabled={!selectedIds.length}
                            className="px-4 py-2 rounded-lg bg-indigo-600 text-white disabled:bg-gray-300"
                        >
                            Wiederherstellen
                        </button>

                        <button
                            onClick={purgeSelected}
                            disabled={!selectedIds.length}
                            className="px-4 py-2 rounded-lg bg-red-600 text-white disabled:bg-gray-300"
                        >
                            Endgültig löschen
                        </button>

                    </div>

                </div>

            </div>

        </div>
    );
}
