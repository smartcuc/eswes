/*
# src/components/device/DeviceChartModal.jsx
*/

import { useState, useEffect, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";

import { apiFetch } from "../../api/client";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
    CartesianGrid,
    ReferenceArea,
    ReferenceLine
} from "recharts";


/* =========================================
   HELPERS
========================================= */

function zoomData(data, start, end) {
    if (!start || !end) return data;

    const startIndex = data.findIndex(d => d.time === start);
    const endIndex = data.findIndex(d => d.time === end);

    if (startIndex === -1 || endIndex === -1) return data;

    return data.slice(
        Math.min(startIndex, endIndex),
        Math.max(startIndex, endIndex) + 1
    );
}

function formatTime(ts) {
    const d = new Date(ts * 1000);
    return d.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}


/* =========================================
   COMPONENT
========================================= */

function DeviceChartModal({ device, onClose }) {

    const [range, setRange] = useState("24h");
    const [live, setLive] = useState(false);

    const [zoom, setZoom] = useState({
        refStart: null,
        refEnd: null,
        start: null,
        end: null,
    });

    /* ✅ ESC schließen */
    useEffect(() => {
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }

        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    /* ✅ DATA */
    const query = useQuery({
        queryKey: ["timeseries", device.id, range],
        queryFn: () =>
            apiFetch(`/api/devices/${device.id}/timeseries/?range=${range}`),
        refetchInterval: live ? 3000 : false
    });

    const data = query.data;

    /* ✅ RAW POINTS */
    const rawPoints = useMemo(() => (
        (data?.points || []).map(p => ({
            time: formatTime(p.t),
            value: Number(p.v ?? 0)
        }))
    ), [data]);

    /* ✅ ZOOM */
    const points = useMemo(() => (
        zoom.start && zoom.end
            ? zoomData(rawPoints, zoom.start, zoom.end)
            : rawPoints
    ), [rawPoints, zoom]);

    const unit = device.unit || "";

    const currentPoint =
        points.length > 0
            ? points[points.length - 1]
            : null;

    /* ✅ Y-BEREICH */
    const { minVal, maxVal } = useMemo(() => {
        if (!points.length) return { minVal: 0, maxVal: 1 };

        const values = points.map(p => p.value);

        return {
            minVal: Math.min(...values),
            maxVal: Math.max(...values)
        };
    }, [points]);

    /* ✅ MIN / MAX PUNKTE */
    const { minPoint, maxPoint } = useMemo(() => {
        if (!points.length) return { minPoint: null, maxPoint: null };

        let minP = points[0];
        let maxP = points[0];

        for (const p of points) {
            if (p.value < minP.value) minP = p;
            if (p.value > maxP.value) maxP = p;
        }

        return {
            minPoint: minP,
            maxPoint: maxP
        };
    }, [points]);

    return (
        <div
            className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
            onClick={onClose}
        >

            <div
                className="
                bg-white
                rounded-2xl
                shadow-xl
                w-full
                max-w-5xl
                h-[80vh]
                flex
                flex-col
                overflow-hidden
            "
                onClick={(e) => e.stopPropagation()}
            >

                {/* HEADER */}

                <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-indigo-50">

                    <div className="flex justify-between items-center">

                        <div>

                            <div className="text-xs text-gray-500">
                                Zeitreihe analysieren
                            </div>

                            <h3 className="font-semibold text-lg text-gray-900">
                                📈 {device.display_name}
                            </h3>

                            <div className="text-xs text-gray-500">
                                {device.identifier}
                            </div>


                            {currentPoint && (
                                <div className="text-sm font-medium text-indigo-600 mt-1">
                                    Aktuell: {currentPoint.value.toFixed(2)} {unit}
                                </div>
                            )}

                        </div>

                        <div className="flex items-center gap-2">

                            <select
                                value={range}
                                onChange={(e) => {
                                    setRange(e.target.value);
                                    setLive(false);
                                    setZoom({
                                        refStart: null,
                                        refEnd: null,
                                        start: null,
                                        end: null
                                    });
                                }}
                                className="border rounded px-2 py-1 text-sm"
                            >
                                <option value="1h">1h</option>
                                <option value="6h">6h</option>
                                <option value="24h">24h</option>
                                <option value="7d">7d</option>
                            </select>

                            <button
                                onClick={() => setLive(v => !v)}
                                className={`px-3 py-1 text-sm rounded ${live
                                    ? "bg-green-500 text-white"
                                    : "bg-gray-200"
                                    }`}
                            >
                                ● LIVE
                            </button>

                            <button
                                onClick={() =>
                                    setZoom({
                                        refStart: null,
                                        refEnd: null,
                                        start: null,
                                        end: null
                                    })
                                }
                                className="px-2 py-1 text-sm bg-gray-100 rounded"
                            >
                                Reset
                            </button>

                            <button
                                onClick={onClose}
                                className="text-gray-400 hover:text-gray-600 text-lg"
                            >
                                ✕
                            </button>

                        </div>

                    </div>

                </div>

                {/* CHART */}

                <div className="flex-1 p-4">

                    <div className="w-full h-full">

                        <ResponsiveContainer
                            width="100%"
                            height="100%"
                        >

                            <LineChart
                                data={points}
                                margin={{
                                    top: 10,
                                    right: 20,
                                    left: 0,
                                    bottom: 0
                                }}

                                onMouseDown={(e) => {
                                    if (e?.activeLabel) {
                                        setZoom(z => ({
                                            ...z,
                                            refStart: e.activeLabel,
                                            refEnd: null
                                        }));
                                    }
                                }}

                                onMouseMove={(e) => {
                                    if (zoom.refStart && e?.activeLabel) {
                                        setZoom(z => ({
                                            ...z,
                                            refEnd: e.activeLabel
                                        }));
                                    }
                                }}

                                onMouseUp={() => {
                                    if (zoom.refStart && zoom.refEnd) {
                                        setZoom(z => ({
                                            ...z,
                                            start: z.refStart,
                                            end: z.refEnd,
                                            refStart: null,
                                            refEnd: null
                                        }));
                                    }
                                }}

                                onDoubleClick={() =>
                                    setZoom({
                                        refStart: null,
                                        refEnd: null,
                                        start: null,
                                        end: null
                                    })
                                }

                                style={{ cursor: "crosshair" }}
                            >


                                {/* ZOOM */}
                                {zoom.refStart && zoom.refEnd && (
                                    <ReferenceArea
                                        x1={zoom.refStart}
                                        x2={zoom.refEnd}
                                        strokeOpacity={0.3}
                                    />
                                )}

                                <CartesianGrid stroke="#f3f4f6" />

                                <XAxis
                                    dataKey="time"
                                    tick={{ fontSize: 12 }}
                                    stroke="#9ca3af"
                                />

                                <YAxis
                                    domain={[minVal * 1.1, maxVal * 1.1]}
                                    tickFormatter={(v) => Math.round(v)}
                                    tick={{ fontSize: 12 }}
                                    stroke="#9ca3af"
                                />

                                <Tooltip
                                    formatter={(value) =>
                                        `${Number(value).toFixed(2)} ${unit}`
                                    }

                                    contentStyle={{
                                        backgroundColor: "#fff",
                                        borderRadius: "8px",
                                        border: "1px solid #e5e7eb"
                                    }}
                                />

                                {/* NULL-LINIE */}

                                {minVal < 0 && maxVal > 0 && (
                                    <ReferenceLine
                                        y={0}
                                        stroke="#6b7280"
                                        strokeDasharray="4 4"
                                        label={{
                                            value: "0",
                                            position: "left",
                                            fill: "#6b7280",
                                            fontSize: 12
                                        }}
                                    />
                                )}

                                {/* MIN LINIE */}
                                {minPoint && (
                                    <ReferenceLine
                                        y={minPoint.value}
                                        stroke="#16a34a"
                                        strokeDasharray="3 3"
                                        label={{
                                            value: `Min ${Math.round(minPoint.value)} ${unit}`,
                                            position: "left",
                                            fill: "#16a34a",
                                            fontSize: 12
                                        }}
                                    />
                                )}

                                {/* MAX LINIE */}
                                {maxPoint && (
                                    <ReferenceLine
                                        y={maxPoint.value}
                                        stroke="#2563eb"
                                        strokeDasharray="3 3"
                                        label={{
                                            value: `Max ${Math.round(maxPoint.value)} ${unit}`,
                                            position: "left",
                                            fill: "#2563eb",
                                            fontSize: 12
                                        }}
                                    />
                                )}

                                {/* ✅ EINE SAUBERE LINIE */}
                                <Line
                                    type="monotone"
                                    dataKey="value"
                                    stroke="#2563eb"
                                    strokeWidth={2}
                                    dot={false}
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />


                            </LineChart>

                        </ResponsiveContainer>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default DeviceChartModal;
