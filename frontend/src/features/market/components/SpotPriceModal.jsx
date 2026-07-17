/*
# src/features/market/components/SpotPriceModal.jsx
*/

import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../../api/client";

export default function SpotPriceModal({
    open,
    onClose,
}) {

    const [range, setRange] = useState("2d");

    const { data } = useQuery({
        queryKey: ["spot-price-chart", range,],
        queryFn: () =>
            apiFetch(
                `/api/market/chart/?range=${range}`
            ),
        enabled: open,
    });

    if (!open) {
        return null;
    }

    return (
        <div
            className="
                fixed inset-0
                bg-black/40
                flex items-center justify-center
                z-50
            "
            onClick={onClose}
        >
            <div
                className="
                    bg-white
                    rounded-2xl
                    p-6
                    w-full
                    max-w-4xl
                "
                onClick={(e) =>
                    e.stopPropagation()
                }
            >

                <h3
                    className="
                        text-xl
                        font-semibold
                        mb-4
                    "
                >
                    ⚡ Spotpreis
                </h3>
                <div className="flex gap-2 mb-5">

                    <button
                        onClick={() => setRange("2d")}
                        className={
                            range === "2d"
                                ? "px-3 py-1 rounded bg-indigo-600 text-white text-sm"
                                : "px-3 py-1 rounded bg-gray-100 text-sm"
                        }
                    >
                        Heute + Morgen
                    </button>

                    <button
                        onClick={() => setRange("today")}
                        className={
                            range === "today"
                                ? "px-3 py-1 rounded bg-indigo-600 text-white text-sm"
                                : "px-3 py-1 rounded bg-gray-100 text-sm"
                        }
                    >
                        Heute
                    </button>

                    <button
                        onClick={() => setRange("tomorrow")}
                        className={
                            range === "tomorrow"
                                ? "px-3 py-1 rounded bg-indigo-600 text-white text-sm"
                                : "px-3 py-1 rounded bg-gray-100 text-sm"
                        }
                    >
                        Morgen
                    </button>

                    <button
                        onClick={() => setRange("5d")}
                        className={
                            range === "5d"
                                ? "px-3 py-1 rounded bg-indigo-600 text-white text-sm"
                                : "px-3 py-1 rounded bg-gray-100 text-sm"
                        }
                    >
                        5 Tage
                    </button>

                </div>

                {data && (
                    <div
                        className="
                            grid
                            grid-cols-4
                            gap-3
                            mb-6
                        "
                    >

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Aktuell
                            </div>

                            <div className="font-semibold text-indigo-600">
                                {data.current?.toFixed(2)} ct
                            </div>
                        </div>

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Minimum
                            </div>

                            <div className="font-semibold text-green-600">
                                {data.min?.toFixed(2)} ct
                            </div>
                        </div>

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Maximum
                            </div>

                            <div className="font-semibold text-red-600">
                                {data.max?.toFixed(2)} ct
                            </div>
                        </div>

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Durchschnitt
                            </div>

                            <div className="font-semibold text-gray-700">
                                {data.avg?.toFixed(2)} ct
                            </div>
                        </div>

                    </div>
                )}
                {data && (
                    <div className="h-[420px]">
                        <ReactECharts
                            option={{
                                tooltip: {
                                    trigger: "axis",
                                    formatter: (params) => {

                                        const p = params[0];

                                        return `
                            <div>
                                <div style="font-size:12px;color:#64748b;">
                                    ${p.name}
                                </div>

                                <div
                                    style="
                                        color:#f59e0b;
                                        font-weight:600;
                                    "
                                >
                                    ${Number(p.value).toFixed(2)} ct/kWh
                                </div>
                            </div>
                        `;
                                    },
                                },

                                grid: {
                                    top: "8%",
                                    left: "4%",
                                    right: "4%",
                                    bottom: "12%",
                                    containLabel: true,
                                },

                                xAxis: {
                                    type: "category",
                                    data: data.timestamps,
                                    boundaryGap: false,
                                },

                                yAxis: {
                                    type: "value",
                                    axisLabel: {
                                        formatter: "{value} ct",
                                    },
                                },

                                series: [
                                    {
                                        name: "Spotpreis",
                                        type: "line",
                                        smooth: true,
                                        showSymbol: false,

                                        data: data.values,

                                        lineStyle: {
                                            color: "#f59e0b",
                                            width: 3,
                                        },

                                        areaStyle: {
                                            opacity: 0.15,
                                            color: "#f59e0b",
                                        },
                                    },
                                ],
                            }}
                            style={{
                                width: "100%",
                                height: "100%",
                            }}
                        />
                    </div>
                )}
            </div>
        </div>
    );
}
