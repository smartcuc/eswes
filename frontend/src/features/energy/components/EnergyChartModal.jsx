/*
# src/features/energy/components/EnergyChartModal.jsx
*/

import { useState, useEffect, useMemo, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";

import { apiFetch } from "../../../api/client";

/* =========================================
   HELPERS
========================================= */

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

export default function EnergyChartModal({ metricKey, displayName, unit, onClose }) {
    const [range, setRange] = useState("24h");
    const [live, setLive] = useState(false);
    const chartRef = useRef(null);

    /* ✅ ESC schließen */
    useEffect(() => {
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    /* ✅ DATA FETCHING (Zentraler EMS-Timeseries Endpoint) */
    const query = useQuery({
        queryKey: ["energy-timeseries", metricKey, range],
        queryFn: () =>
            apiFetch(`/api/energy/timeseries/?metric=${metricKey}&range=${range}`),
        refetchInterval: live ? 3000 : false
    });

    const data = query.data;

    /* ✅ DATA FORMATTING FOR ECHARTS */
    const chartData = useMemo(() => {
        const points = data?.points || [];
        const xAxisData = [];
        const seriesData = [];

        points.forEach(p => {
            xAxisData.push(formatTime(p.t));
            seriesData.push(Number(p.v ?? 0));
        });

        return { xAxisData, seriesData };
    }, [data]);

    const currentPointValue = chartData.seriesData.length > 0
        ? chartData.seriesData[chartData.seriesData.length - 1]
        : null;

    const handleResetZoom = () => {
        if (chartRef.current) {
            chartRef.current.getEchartsInstance().dispatchAction({
                type: 'dataZoom',
                start: 0,
                end: 100
            });
        }
    };

    /* ✅ ECHARTS OPTIONS CONFIGURATION */
    const option = useMemo(() => {
        const mainColor = '#0ea5e9'; // Edles Energie-Cyan-Blau

        return {
            tooltip: {
                trigger: 'axis',
                formatter: (params) => {
                    const p = params[0];
                    return `${p.name}<br/><span style="color:${mainColor};font-weight:bold;">${Number(p.value).toFixed(2)} ${unit}</span>`;
                },
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                textStyle: { color: '#1e293b' }
            },
            grid: {
                top: '6%',
                left: '3%',
                right: '4%',
                bottom: '15%',
                containLabel: true
            },
            xAxis: {
                type: 'category',
                data: chartData.xAxisData,
                boundaryGap: false,
                axisLine: { lineStyle: { color: '#cbd5e1' } },
                axisLabel: { color: '#64748b' }
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                axisLabel: {
                    color: '#64748b',
                    formatter: (value) => `${Number(value).toFixed(2)} ${unit}`
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },
            dataZoom: [
                { type: 'inside', start: 0, end: 100 },
                {
                    type: 'slider',
                    start: 0,
                    end: 100,
                    foregroundColor: mainColor,
                    textStyle: { color: '#64748b' },
                    borderColor: '#f1f5f9'
                }
            ],
            series: [
                {
                    name: displayName,
                    type: 'line',
                    data: chartData.seriesData,
                    showSymbol: false,
                    smooth: true,
                    lineStyle: { color: mainColor, width: 2.5 },
                    areaStyle: {
                        color: {
                            type: 'linear', x: 0, y: 0, x2: 0, y2: 1,
                            colorStops: [
                                { offset: 0, color: 'rgba(14, 165, 233, 0.15)' },
                                { offset: 1, color: 'rgba(14, 165, 233, 0.0)' }
                            ]
                        }
                    },
                    markLine: {
                        symbol: ['none', 'none'],
                        silent: true,
                        data: [
                            // MAX LINE (Edles Orange-Rot)
                            {
                                type: 'max',
                                name: 'Max',
                                lineStyle: { color: '#f97316', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start',
                                    formatter: (params) => `Max: ${Number(params.value).toFixed(2)} ${unit}`,
                                    backgroundColor: '#fff7ed',
                                    borderColor: '#ffedd5',
                                    borderWidth: 1,
                                    //padding:,
                                    borderRadius: 4,
                                    color: '#c2410c',
                                    fontSize: 10
                                }
                            },
                            // MIN LINE (Weiches Slate-Grau)
                            {
                                type: 'min',
                                name: 'Min',
                                lineStyle: { color: '#64748b', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start',
                                    formatter: (params) => `Min: ${Number(params.value).toFixed(2)} ${unit}`,
                                    backgroundColor: '#f8fafc',
                                    borderColor: '#e2e8f0',
                                    borderWidth: 1,
                                    //padding:,
                                    borderRadius: 4,
                                    color: '#334155',
                                    fontSize: 10
                                }
                            },
                            // AVERAGE LINE (Dezent, Randlos rechts)
                            {
                                type: 'average',
                                name: 'Schnitt',
                                lineStyle: { color: '#cbd5e1', type: 'dotted', width: 1 },
                                label: {
                                    position: 'end',
                                    formatter: (params) => `Ø: ${Number(params.value).toFixed(2)} ${unit}`,
                                    color: '#94a3b8',
                                    fontSize: 10,
                                    backgroundColor: 'transparent',
                                    borderWidth: 0
                                }
                            }
                        ]
                    }
                }
            ]
        };
    }, [chartData, unit, displayName]);

    return (
        <div
            className="fixed inset-0 bg-black/40 flex items-center justify-center z-50"
            onClick={onClose}
        >
            <div
                className="bg-white rounded-2xl shadow-xl w-full max-w-5xl h-[80vh] flex flex-col overflow-hidden"
                onClick={(e) => e.stopPropagation()}
            >
                {/* HEADER */}
                <div className="p-4 border-b bg-gradient-to-r from-blue-50 to-indigo-50">
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="text-xs text-gray-500">EMS System-Analyse</div>
                            <h3 className="font-semibold text-lg text-gray-900">⚡ {displayName}</h3>

                            {currentPointValue !== null && (
                                <div className="text-sm font-medium text-sky-600 mt-1">
                                    Aktueller Live-Wert: {currentPointValue.toFixed(2)} {unit}
                                </div>
                            )}
                        </div>

                        <div className="flex items-center gap-2">
                            <select
                                value={range}
                                onChange={(e) => {
                                    setRange(e.target.value);
                                    setLive(false);
                                }}
                                className="border rounded px-2 py-1 text-sm bg-white"
                            >
                                <option value="1h">1h</option>
                                <option value="6h">6h</option>
                                <option value="24h">24h</option>
                                <option value="7d">7d</option>
                            </select>

                            <button
                                onClick={() => setLive(v => !v)}
                                className={`px-3 py-1 text-sm rounded font-medium transition-colors ${live ? "bg-green-500 text-white" : "bg-gray-200 text-gray-700"
                                    }`}
                            >
                                ● LIVE
                            </button>

                            <button
                                onClick={handleResetZoom}
                                className="px-2 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded text-gray-600"
                            >
                                Reset
                            </button>

                            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-lg p-1">
                                ✕
                            </button>
                        </div>
                    </div>
                </div>

                {/* CHART CONTAINER */}
                <div className="flex-1 p-4 relative min-h-0">
                    <ReactECharts
                        ref={chartRef}
                        option={option}
                        style={{ width: "100%", height: "100%" }}
                        notMerge={true}
                        lazyUpdate={true}
                    />
                </div>
            </div>
        </div>
    );
}
