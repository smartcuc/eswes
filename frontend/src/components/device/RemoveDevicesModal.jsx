/*
# src/components/device/RemoveDevicesModal.jsx
*/

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { apiFetch } from "../../api/client";

export default function RemoveDevicesModal({
    open,
    onClose,
}) {

    const queryClient = useQueryClient();

    const [selectedIds, setSelectedIds] = useState([]);

    const devicesQuery = useQuery({
        queryKey: ["devices"],
        queryFn: () => apiFetch("/api/devices/"),
        enabled: open,
    });

    if (!open) {
        return null;
    }

    const devices = devicesQuery.data ?? [];

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

    async function handleDelete() {

        if (selectedIds.length === 0) {
            return;
        }

        const confirmed = window.confirm(
            `${selectedIds.length} Gerät(e) in den Papierkorb verschieben?`
        );

        if (!confirmed) {
            return;
        }

        try {

            await apiFetch("/api/devices/remove/", {
                method: "POST",
                body: JSON.stringify({
                    device_ids: selectedIds,
                }),
            });

            await queryClient.invalidateQueries({
                queryKey: ["devices"],
            });

            setSelectedIds([]);

            onClose();

        } catch (err) {

            console.error(err);

            alert("Fehler beim Entfernen.");
        }
    }

    return (
        <div className="fixed inset-0 z-50 bg-black/30 flex items-center justify-center">

            <div className="bg-white rounded-xl shadow-xl w-full max-w-2xl">

                <div className="p-4 border-b flex justify-between items-center">

                    <h2 className="font-semibold text-lg">
                        Geräte löschen
                    </h2>

                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-gray-600"
                    >
                        ✕
                    </button>

                </div>

                <div className="p-4">

                    {devicesQuery.isLoading ? (
                        <div>Lade Geräte...</div>
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

                            <div className="border rounded-lg overflow-hidden max-h-[500px] overflow-y-auto">

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

                                        <div>

                                            <div className="font-medium">
                                                {device.display_name}
                                            </div>

                                            <div className="text-xs text-gray-500">
                                                {device.identifier}
                                            </div>

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
                            onClick={onClose}
                            className="px-4 py-2 border rounded-lg"
                        >
                            Abbrechen
                        </button>

                        <button
                            onClick={handleDelete}
                            disabled={selectedIds.length === 0}
                            className="px-4 py-2 rounded-lg bg-red-600 text-white disabled:bg-gray-300"
                        >
                            Löschen
                        </button>

                    </div>

                </div>

            </div>

        </div>
    );
}