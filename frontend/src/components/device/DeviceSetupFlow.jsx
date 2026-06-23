/*
# src/components/device/DeviceSetupFlow.jsx
*/

import { useState } from "react";

export default function DeviceSetupFlow({ device, onDone }) {

    const [type, setType] = useState(null);
    const [metrics, setMetrics] = useState([]);
    const [loading, setLoading] = useState(false);

    const typeOptions = [
        ["heatpump", "Wärmepumpe"],
        ["pv", "PV Anlage"],
        ["battery", "Batterie"],
        ["meter", "Zähler"],
        ["other", "Sonstiges"]
    ];

    const metricOptions = [
        ["power", "Strom"],
        ["temperature", "Temperatur"],
        ["status", "Status"],
        ["energy", "Energie"]
    ];

    function toggleMetric(m) {
        setMetrics((prev) =>
            prev.includes(m)
                ? prev.filter(x => x !== m)
                : [...prev, m]
        );
    }

    async function save() {
        try {
            setLoading(true);

            await fetch(`/api/devices/by-id/${device.id}/configure/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${localStorage.getItem("token")}`
                },
                body: JSON.stringify({
                    type,
                    metrics
                })
            });

            onDone();

        } catch (e) {
            alert("Fehler beim Speichern");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="p-6 max-w-md mx-auto">

            <h2 className="text-lg font-semibold mb-4">
                Gerät einrichten
            </h2>

            {/* TYPE */}
            <div className="mb-6">
                <h3 className="text-sm text-gray-500 mb-2">
                    Was ist das für ein Gerät?
                </h3>

                <div className="space-y-2">
                    {typeOptions.map(([key, label]) => (
                        <button
                            key={key}
                            onClick={() => setType(key)}
                            className={`w-full p-3 rounded border ${type === key
                                    ? "bg-indigo-100 border-indigo-500"
                                    : "bg-white"
                                }`}
                        >
                            {label}
                        </button>
                    ))}
                </div>
            </div>

            {/* METRICS */}
            <div className="mb-6">
                <h3 className="text-sm text-gray-500 mb-2">
                    Was misst das Gerät?
                </h3>

                <div className="space-y-2">
                    {metricOptions.map(([key, label]) => (
                        <label key={key} className="flex items-center gap-2">
                            <input
                                type="checkbox"
                                checked={metrics.includes(key)}
                                onChange={() => toggleMetric(key)}
                            />
                            {label}
                        </label>
                    ))}
                </div>
            </div>

            {/* ACTION */}
            <button
                onClick={save}
                disabled={!type || loading}
                className="w-full bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
            >
                {loading ? "Speichere..." : "Gerät fertig einrichten"}
            </button>

        </div>
    );
}
