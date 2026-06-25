/*
# src/pages/DevicesPage.jsx
*/

import { useUnconfiguredDevices } from "../hooks/useUnconfiguredDevices";
import { useDeviceRoles } from "../hooks/useDeviceMeta";

import { apiFetch } from "../api/client";

export default function DevicesPage() {

    const query = useUnconfiguredDevices();
    const devices = query?.data?.devices || [];

    const rolesQuery = useDeviceRoles();

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
                        key={device.config.id}
                        className="bg-white border rounded p-4 flex items-center gap-4"
                    >

                        {/* NAME */}
                        <div className="flex-1">
                            <div className="font-medium">
                                {device.config.name || `Device ${device.config.id}`}
                            </div>

                            <div className="text-xs text-gray-400">
                                {device.config.identifier}
                            </div>
                        </div>

                        {/* TYPE */}
                        <select
                            value={device.config.type?.key || ""}
                            onChange={(e) =>
                                updateDevice(device.config.id, "type", e.target.value)
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
                            value={device.config.role?.key || ""}
                            onChange={(e) =>
                                updateDevice(device.config.id, "role", e.target.value)
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
