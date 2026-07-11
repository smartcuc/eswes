/*
# src/features/energy/components/EnergyChartModal.jsx
*/
import { useState, useEffect, useMemo, useRef, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../../api/client";

/* =========================================
 COMPONENT
========================================= */
export default function EnergyChartModal({
    metricKey,
    displayName,
    unit,
    color = "#0ea5e9",
    onClose,
}) {
    const [range, setRange] = useState("24h");
    const [live, setLive] = useState(false);
    const [isZoomed, setIsZoomed] = useState(false);
    const chartRef = useRef(null);

    /* ✅ ESC schließen */
    useEffect(() => {
        const handleKey = (e) => {
            if (e.key === "Escape") onClose();
        };
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    /* ✅ DATA FETCHING (Zentraler EMS-Timeseries Endpoint) */
    const { data } = useQuery({
        queryKey: ["energy-chart", metricKey, range],
        queryFn: () => apiFetch(`/api/energy/chart/?metric=${metricKey}&period=${range}`),
        refetchInterval: live ? 3000 : false,
    });

    // Direkte, schlanke Zuweisung (ersetzt das verschachtelte useMemo)
    const xAxisData = data?.timestamps || [];
    const seriesData = data?.values || [];

    const currentPointValue = seriesData.length > 0
        ? seriesData[seriesData.length - 1]
        : null;

    /* ✅ ZOOM CONTROLS */
    const handleResetZoom = () => {
        if (chartRef.current) {
            chartRef.current.getEchartsInstance().dispatchAction({
                type: "dataZoom",
                start: 0,
                end: 100,
            });
            setIsZoomed(false);
        }
    };

    // Callback stabilisiert die Event-Referenz (Verhindert Re-Renders)
    const handleDataZoom = useCallback((event) => {
        const start = event.batch?.[0]?.start ?? event.start ?? 0;
        const end = event.batch?.[0]?.end ?? event.end ?? 100;
        setIsZoomed(start > 0 || end < 100);
    }, []);

    const onEvents = useMemo(() => ({
        datazoom: handleDataZoom
    }), [handleDataZoom]);

    /* ✅ ECHARTS OPTIONS CONFIGURATION */
    const option = useMemo(() => {
        const mainColor = color;

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
                data: xAxisData,
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
                    data: seriesData,
                    showSymbol: false,
                    smooth: true,
                    lineStyle: { color: mainColor, width: 2.5 },
                    areaStyle: {
                        color: {
                            type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                            colorStops: [
                                { offset: 0, color: `${mainColor}33` },
                                { offset: 1, color: `${mainColor}00` },
                            ],
                        },
                    },
                    markLine: {
                        symbol: ['none', 'none'],
                        silent: true,
                        data: [
                            {
                                type: 'max',
                                name: 'Max',
                                lineStyle: { color: '#f97316', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start',
                                    formatter: (params) => `Max: ${Number(params.value).toFixed(2)} ${unit} `,
                                    backgroundColor: '#fff7ed', borderColor: '#ffedd5', borderWidth: 1,
                                    borderRadius: 4, color: '#c2410c', fontSize: 10
                                }
                            },
                            {
                                type: 'min',
                                name: 'Min',
                                lineStyle: { color: '#64748b', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start',
                                    formatter: (params) => `Min: ${Number(params.value).toFixed(2)} ${unit} `,
                                    backgroundColor: '#f8fafc', borderColor: '#e2e8f0', borderWidth: 1,
                                    borderRadius: 4, color: '#334155', fontSize: 10
                                }
                            },
                            {
                                type: 'average',
                                name: 'Schnitt',
                                lineStyle: { color: '#cbd5e1', type: 'dotted', width: 1 },
                                label: {
                                    position: 'end',
                                    formatter: (params) => `Ø: ${Number(params.value).toFixed(2)} ${unit} `,
                                    color: '#94a3b8', fontSize: 10, backgroundColor: 'transparent', borderWidth: 0
                                }
                            }
                        ]
                    }
                }
            ]
        };
    }, [color, unit, displayName, xAxisData, seriesData]);

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
                <div
                    className="p-4 border-b"
                    style={{ background: `linear-gradient(135deg, ${color}30, ${color}08)` }}
                >
                    <div className="flex justify-between items-center">
                        {/* LINKS */}
                        <div>
                            <div className="text-xs text-gray-500">EMS System-Analyse</div>
                            <h3 className="font-semibold text-lg" style={{ color }}>
                                {displayName} ⚡
                            </h3>
                            {currentPointValue !== null && (
                                <div className="text-sm font-medium mt-1" style={{ color }}>
                                    Aktueller Live-Wert: {currentPointValue.toFixed(2)} {unit}
                                </div>
                            )}
                        </div>

                        {/* RECHTS */}
                        <div className="flex items-center gap-2">
                            {range === "1h" && (
                                <button
                                    onClick={() => setLive((v) => !v)}
                                    className={`px-3 py-1 text-sm rounded-lg font-medium transition-colors flex items-center gap-2 ${live ? "bg-green-500 text-white" : "bg-gray-100 text-gray-700"
                                        }`}
                                >
                                    <span className={`inline-block w-2 h-2 rounded-full ${live ? "bg-white animate-pulse" : "bg-gray-400"
                                        }`} />
                                    Live
                                </button>
                            )}

                            {/* Perioden-Auswahl mit dynamischen Tailwind-Klassen */}
                            <div className="flex rounded-lg overflow-hidden border shadow-sm bg-white">
                                {["1h", "6h", "24h", "5d"].map((period) => (
                                    <button
                                        key={period}
                                        onClick={() => {
                                            setRange(period);
                                            if (period !== "1h") setLive(false);
                                        }}
                                        className={`px-3 py-1 text-sm font-medium transition-colors ${range === period
                                            ? "text-white"
                                            : "text-gray-500 hover:bg-gray-50"
                                            }`}
                                        style={range === period ? { backgroundColor: color } : undefined}
                                    >
                                        {period}
                                    </button>
                                ))}
                            </div>

                            {/* Export-Buttons (Kompakte Schleife) */}
                            {["csv", "xlsx", "pdf"].map((ext) => (
                                <button
                                    key={ext}
                                    onClick={() => window.open(`/api/energy/chart/export/${ext}/?metric=${metricKey}&period=${range}`, "_blank")}
                                    className="px-3 py-1 text-sm rounded-lg text-white shadow-sm font-medium uppercase transition-opacity hover:opacity-90"
                                    style={{ backgroundColor: color }}
                                >
                                    {ext}
                                </button>
                            ))}

                            {isZoomed && (
                                <button
                                    onClick={handleResetZoom}
                                    className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg text-gray-600 font-medium transition-colors"
                                >
                                    Reset
                                </button>
                            )}
                            <button onClick={onClose} className="text-gray-400 hover:text-gray-600 text-lg p-1 transition-colors">✕</button>
                        </div>
                    </div>
                </div>

                {/* CHART CONTAINER */}
                <div className="flex-1 p-4 relative min-h-0">
                    <ReactECharts
                        ref={chartRef}
                        option={option}
                        onEvents={onEvents}
                        style={{ width: "100%", height: "100%" }}
                        notMerge={true}
                        lazyUpdate={true}
                    />
                </div>
            </div>
        </div>
    );
}