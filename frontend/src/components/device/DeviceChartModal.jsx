/*
# src/components/device/DeviceChartModal.jsx
*/

import { useState, useEffect, useMemo, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";

import { apiFetch } from "../../api/client";

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

function getDeviceStyle(device) {

    const config = device.config || {};

    if (config.is_grid_source) {
        return {
            color: "#10b981",
            icon: "🔌",
        };
    }

    switch (config.role?.key) {

        case "producer":
            return {
                color: "#f59e0b",
                icon: "☀️",
            };

        case "consumer":
            return {
                color: "#2563eb",
                icon: "⚡",
            };

        case "battery":
            return {
                color: "#8b5cf6",
                icon: "🔋",
            };

        default:
            return {
                color: "#64748b",
                icon: "🔧",
            };
    }
}


/* =========================================
   COMPONENT
========================================= */

function DeviceChartModal({ device, onClose }) {
    const [range, setRange] = useState("24h");
    const [live, setLive] = useState(false);
    const chartRef = useRef(null);
    const deviceStyle = getDeviceStyle(device);
    const mainColor = deviceStyle.color;

    /* ✅ ESC schließen */
    useEffect(() => {
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    /* ✅ DATA FETCHING */
    const query = useQuery({
        queryKey: ["timeseries", device.id, range],
        queryFn: () =>
            apiFetch(`/api/devices/${device.id}/timeseries/?range=${range}`),
        refetchInterval: live ? 3000 : false
    });

    const data = query.data;
    const unit = device.unit || "";

    /* ✅ DATA FORMATTING FOR ECHARTS */
    // ECharts arbeitet am besten mit zwei separaten Arrays für X und Y
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

    // Aktuellen Punkt für den Header ermitteln
    const currentPointValue = chartData.seriesData.length > 0
        ? chartData.seriesData[chartData.seriesData.length - 1]
        : null;

    /* ✅ NATIVES RESET */
    const handleResetZoom = () => {
        if (chartRef.current) {
            const chartInstance = chartRef.current.getEchartsInstance();
            // Setzt den Zoom-Schieberegler wieder auf 0% - 100%
            chartInstance.dispatchAction({
                type: 'dataZoom',
                start: 0,
                end: 100
            });
        }
    };

    /* ✅ ECHARTS OPTIONS CONFIGURATION */
    const option = useMemo(() => {
        return {
            // Schickes, reaktionsschnelles Tooltip
            tooltip: {
                trigger: 'axis',
                formatter: function (params) {
                    const p = params[0];
                    return `${p.name}<br/><span style="color:#6366f1;font-weight:bold;">${Number(p.value).toFixed(2)} ${unit}</span>`;
                },
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                textStyle: { color: '#1e293b' }
            },
            grid: {
                top: '4%',
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
                    // 💡 Rundet die Achsenbeschriftung auf 2 Nachkommastellen
                    formatter: (value) => `${Number(value).toFixed(2)} ${unit}`
                },
                splitLine: { lineStyle: { color: '#f1f5f9' } }
            },

            // 💡 NATIVE ZOOM ENGINE (Ersetzt die Recharts Maus-Events komplett!)
            dataZoom: [
                {
                    type: 'inside', // Erlaubt Scrollen/Pinchen direkt im Chart
                    start: 0,
                    end: 100
                },
                {
                    type: 'slider', // Der sichtbare Schieberegler unten
                    start: 0,
                    end: 100,
                    foregroundColor: '#6366f1',
                    textStyle: { color: '#64748b' },
                    borderColor: '#f1f5f9'
                }
            ],
            series: [
                {
                    name: device.display_name,
                    type: 'line',
                    data: chartData.seriesData,
                    showSymbol: false,
                    smooth: true, // Macht die Kurve elegant weich
                    lineStyle: {
                        // color: '#6366f1',
                        color: mainColor,
                        width: 2.5
                    },
                    // Hübscher Farbverlauf unter der Linie
                    areaStyle: {
                        color: {
                            type: 'linear',
                            x: 0, y: 0, x2: 0, y2: 1,
                            colorStops: [
                                //  { offset: 0, color: 'rgba(99, 102, 241, 0.2)' },
                                //  { offset: 1, color: 'rgba(99, 102, 241, 0.0)' }
                                { offset: 0, color: 'rgba(14, 165, 233, 0.15)' }, // Sanfter Verlauf
                                { offset: 1, color: 'rgba(14, 165, 233, 0.0)' }
                            ]
                        }
                    },
                    // 📈 Automatische Min/Max Punkte im Chart markieren
                    markPoint: null,

                    // 💡 2. Neues `markLine` für gepunktete Linien zur Y-Achse
                    markLine: {
                        symbol: ['none', 'none'], // Entfernt Pfeile an den Linienenden
                        silent: true,            // Maus-Events für Linien deaktivieren
                        data: [
                            {
                                type: 'max',
                                name: 'Max',
                                //lineStyle: { color: '#ef4444', type: 'dashed', width: 1 }, // Rot gepunktet
                                lineStyle: { color: '#f97316', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start', // Platziert den Text direkt an der Y-Achse
                                    formatter: (params) => `Max: ${Number(params.value).toFixed(2)} ${unit}`,
                                    //backgroundColor: '#fef2f2',                        
                                    //borderColor: '#fee2e2',
                                    backgroundColor: '#fff7ed',
                                    borderColor: '#ffedd5',
                                    borderWidth: 1,
                                    // padding:,
                                    borderRadius: 4,
                                    //color: '#991b1b',
                                    color: '#c2410c',
                                    fontSize: 10
                                }
                            },
                            {
                                type: 'min',
                                name: 'Min',
                                //lineStyle: { color: '#06b6d4', type: 'dashed', width: 1 }, // Cyan gepunktet
                                lineStyle: { color: '#64748b', type: 'dashed', width: 1 },
                                label: {
                                    position: 'start',
                                    formatter: (params) => `Min: ${Number(params.value).toFixed(2)} ${unit}`,
                                    //backgroundColor: '#ecfeff',
                                    //borderColor: '#cffafe',
                                    backgroundColor: '#f8fafc',
                                    borderColor: '#e2e8f0',
                                    borderWidth: 1,
                                    // padding:,
                                    borderRadius: 4,
                                    //color: '#155e75',
                                    color: '#334155',
                                    fontSize: 10
                                }
                            },
                            {
                                type: 'average',
                                name: 'Schnitt',
                                //lineStyle: { color: '#94a3b8', type: 'dashed', width: 1 },
                                lineStyle: { color: '#cbd5e1', type: 'dotted', width: 1 },
                                label: {
                                    position: 'end', // Am rechten Rand des Charts platzieren
                                    formatter: (params) => `Ø: ${Number(params.value).toFixed(2)} ${unit}`,
                                    backgroundColor: '#f8fafc',
                                    borderColor: '#e2e8f0',
                                    borderWidth: 1,
                                    padding: 4,
                                    borderRadius: 4,
                                    //color: '#475569',
                                    color: '#94a3b8',
                                    fontSize: 10
                                }
                            }
                        ]

                    },
                }
            ]
        };
    }, [chartData, unit, device.display_name]);

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
                    style={{
                        background: `linear-gradient(
                            135deg,
                            ${mainColor}30,
                            ${mainColor}08
                        )`
                    }}
                >
                    <div className="flex justify-between items-center">
                        <div>
                            <div className="text-xs text-gray-500">Zeitreihe analysieren</div>
                            <h3 className="font-semibold text-lg text-gray-900">{deviceStyle.icon} {device.display_name}</h3>
                            <div className="text-xs text-gray-500">{device.identifier}</div>

                            {currentPointValue !== null && (
                                <div
                                    className="text-sm font-medium mt-1"
                                    style={{ color: mainColor }}
                                >
                                    Aktuell: {currentPointValue.toFixed(2)} {unit}
                                </div>
                            )}
                            `
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

                            <button
                                onClick={onClose}
                                className="text-gray-400 hover:text-gray-600 text-lg p-1"
                            >
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
                        notMerge={true} // Verhindert Daten-Reste beim Range-Wechsel
                        lazyUpdate={true}
                    />
                </div>
            </div>
        </div>
    );
}

export default DeviceChartModal;
