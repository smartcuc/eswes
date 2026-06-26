/*
# src/components/device/DeviceChartModal.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import { apiFetch } from "../api/client";


export default function DeviceChartModal({ device, onClose }) {

    const { data } = useQuery({
        queryKey: ["timeseries", device.id],
        queryFn: () => apiFetch(`/api/devices/${device.id}/timeseries/?range=24h`)
    });

    const points = (data?.points || []).map(p => ({
        time: new Date(p.t * 1000).toLocaleTimeString(),
        value: p.v
    }));

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">

            <div className="bg-white p-6 rounded-xl w-full max-w-2xl">

                <h3 className="mb-4 font-semibold">
                    {device.display_name}
                </h3>

                <div style={{ width: "100%", height: 300 }}>

                    <ResponsiveContainer>
                        <LineChart data={points}>

                            <XAxis dataKey="time" />
                            <YAxis />
                            <Tooltip />

                            <Line
                                type="monotone"
                                dataKey="value"
                                stroke="#6366f1"
                                dot={false}
                            />

                        </LineChart>
                    </ResponsiveContainer>

                </div>

                <button
                    onClick={onClose}
                    className="mt-4 bg-gray-200 px-3 py-1 rounded"
                >
                    Schließen
                </button>

            </div>

        </div>
    );
}
