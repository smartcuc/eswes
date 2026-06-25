/*
# src/pages/DevicesPage.jsx
*/

import { useUnconfiguredDevices } from "../hooks/useUnconfiguredDevices";
import { useDeviceTypes, useDeviceRoles } from "../hooks/useDeviceMeta";

import { apiFetch } from "../api/client";

export default function DevicesPage() {

    const query = useUnconfiguredDevices();
    const devices = query?.data?.devices || [];

    const typesQuery = useDeviceTypes();
    const rolesQuery = useDeviceRoles();

    const types = typesQuery.data || [];
    const roles = rolesQuery.data || [];

    async function updateDevice(id, field, value) {
        await apiFetch(`/api/devices/${id}/`, {
            method: "PATCH",
            body: JSON.stringify({
                [field]: value,
            }),
        });

        await query.refetch();
    }

    return (
        <div className="p-6 max-w-4xl">

            <h1 className="text-2xl font-semibold mb-6">
                Geräte
            </h1>

            {devices.length === 0 && (
                <div className="text-gray-500">
                    ✅ Alle Geräte sind konfiguriert
                </div>
            )}

            <div className="space-y-4">

                {devices.map((device) => (
                    <div
                        key={device.id}
                        className="bg-white border rounded p-4 flex items-center gap-4"
                    >

                        {/* NAME */}
                        <div className="flex-1">
                            <div className="font-medium">
                                {device.name || `Device ${device.id}`}
                            </div>

                            <div className="text-xs text-gray-400">
                                {device.identifier}
                            </div>
                        </div>

                        {/* TYPE */}
                        <select
                            value={device.type?.key || ""}
                            onChange={(e) =>
                                updateDevice(device.id, "type", e.target.value)
                            }
                            className="border rounded px-2 py-1 text-sm"
                        >
                            <option value="">Type wählen</option>

                            {types.map((t) => (
                                <option key={t.key} value={t.key}>
                                    {t.name}
                                </option>
                            ))}
                        </select>

                        {/* ROLE */}
                        <select
                            value={device.role?.key || ""}
                            onChange={(e) =>
                                updateDevice(device.id, "role", e.target.value)
                            }
                            className="border rounded px-2 py-1 text-sm"
                        >
                            <option value="">Role wählen</option>

                            {roles.map((r) => (
                                <option key={r.key} value={r.key}>
                                    {r.name}
                                </option>
                            ))}
                        </select>

                    </div>
                ))}

            </div>

        </div>
    );
}
