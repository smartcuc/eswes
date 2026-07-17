/*
# src/features/market/components/SpotPriceModal.jsx
*/
import { useState, useEffect, useMemo, useRef, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import ReactECharts from "echarts-for-react";
import { apiFetch } from "../../../api/client";

export default function SpotPriceModal({
    open,
    onClose,
}) {
    const [range, setRange] = useState("2d");
    const [zoomRange, setZoomRange] = useState({ start: 0, end: 100 });
    const [isZoomed, setIsZoomed] = useState(false); // ✅ FIX: Fehlender State hinzugefügt
    const chartRef = useRef(null); // ✅ FIX: Fehlende Referenz hinzugefügt

    /* ✅ ESC schließen */
    useEffect(() => {
        function handleKey(e) {
            if (e.key === "Escape") onClose();
        }
        window.addEventListener("keydown", handleKey);
        return () => window.removeEventListener("keydown", handleKey);
    }, [onClose]);

    /* ✅ DATA FETCHING */
    const { data } = useQuery({
        queryKey: ["spot-price-chart", range],
        queryFn: () => apiFetch(`/api/market/chart/?range=${range}`),
        enabled: open,
    });

    /* ✅ FIX: Daten-Mapping für ECharts (Sicheres Auslesen aus dem API) */
    const chartData = useMemo(() => {
        return {
            xAxisData: data?.timestamps || [],
            seriesData: data?.values || []
        };
    }, [data]);

    /* ✅ REAKTIVE STATS (Präzise Berechnung der sichtbaren Punkte) */
    const liveStats = useMemo(() => {
        const values = chartData.seriesData; // ✅ FIX: Existiert jetzt durch das Mapping oben
        if (!values || values.length === 0) {
            return { min: 0, max: 0, avg: 0 };
        }

        // Berechne die echten Array-Grenzen anhand der Zoom-Prozentwerte
        const startIndex = Math.max(0, Math.floor((zoomRange.start / 100) * values.length));
        const endIndex = Math.min(values.length, Math.ceil((zoomRange.end / 100) * values.length));

        // Hole exakt den sichtbaren Ausschnitt
        const visibleValues = values.slice(startIndex, endIndex);

        if (visibleValues.length === 0) {
            const fallback = values[values.length - 1] || 0;
            return { min: fallback, max: fallback, avg: fallback };
        }

        const min = Math.min(...visibleValues);
        const max = Math.max(...visibleValues);
        const avg = visibleValues.reduce((a, b) => a + b, 0) / visibleValues.length;

        return { min, max, avg };
    }, [chartData, zoomRange]);

    /* ✅ ABSOLUT SICHERES ECHARTS ZOOM-EVENT */
    const handleDataZoom = useCallback((event) => {
        if (!chartRef.current) return;

        // Hole die echten, aktuellen Zoom-Prozentwerte direkt aus der Chart-Instanz
        const chartInstance = chartRef.current.getEchartsInstance();
        const optionObj = chartInstance.getOption();
        const dataZoom = optionObj.dataZoom?.find(
            z => z.start !== undefined
        );

        if (dataZoom) {
            const start = dataZoom.start ?? 0;
            const end = dataZoom.end ?? 100;

            setZoomRange({ start, end });
            setIsZoomed(start > 0 || end < 100);
        }
    }, []);

    // onEvents greift sauber auf das weiter oben deklarierte handleDataZoom zu
    const onEvents = useMemo(() => ({
        datazoom: handleDataZoom,
    }), [handleDataZoom]);

    /* ✅ NATIVES RESET (Wenn der Nutzer den Zoom zurücksetzt) */
    const handleResetZoom = () => {
        if (chartRef.current) {
            const chartInstance = chartRef.current.getEchartsInstance();
            chartInstance.dispatchAction({
                type: 'dataZoom',
                start: 0,
                end: 100
            });
            setZoomRange({ start: 0, end: 100 }); // Stats zurücksetzen
            setIsZoomed(false);
        }
    };

    /* ✅ ECHARTS OPTIONS CONFIGURATION (Vorbereitet für dein File) */
    const option = useMemo(() => {
        const mainColor = "#0ea5e9"; // Standard-Marktfarbe (Cyan), kannst du anpassen

        return {
            tooltip: {
                trigger: 'axis',
                formatter: (params) => {
                    const p = params[0]; // Sichert ab, dass ECharts wegen Array-Struktur nicht crasht
                    if (!p) return "";
                    return `${p.name}<br/><span style="color:${mainColor};font-weight:bold;">${Number(p.value).toFixed(2)} ct/kWh</span>`;
                },
                backgroundColor: 'rgba(255, 255, 255, 0.95)',
                borderColor: '#e2e8f0',
                borderWidth: 1,
                textStyle: { color: '#1e293b' }
            },
            grid: { top: '8%', left: '3%', right: '4%', bottom: '15%', containLabel: true },
            xAxis: {
                type: 'category',
                data: chartData.xAxisData,
                axisLine: { lineStyle: { color: '#cbd5e1' } },
                axisLabel: { color: '#64748b' }
            },
            yAxis: {
                type: 'value',
                axisLine: { show: false },
                axisLabel: { color: '#64748b', formatter: (value) => `${Number(value).toFixed(1)} ct` },
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
                    name: "Börsenstrompreis",
                    type: "line",
                    data: chartData.seriesData,
                    showSymbol: false,
                    smooth: true,
                    lineStyle: { color: mainColor, width: 2.5 },
                    areaStyle: {
                        color: {
                            type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                            colorStops: [
                                { offset: 0, color: `${mainColor}25` },
                                { offset: 1, color: `${mainColor}00` },
                            ],
                        },
                    }
                }
            ]
        };
    }, [chartData]);

    // ✅ FIX: Der Modal-Guard steht jetzt regelkonform GANZ unten vor dem Return
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
                <div
                    className="p-4 border-b"
                    style={{
                        background: `
                        linear-gradient(
                            135deg,
                            rgba(245,158,11,.20),
                            rgba(245,158,11,.05)
                        )
                    `
                    }}
                >

                    <div className="flex justify-between items-center">

                        <div>

                            <div className="text-xs text-gray-500">
                                Spotmarkt analysieren
                            </div>

                            <h3 className="font-semibold text-lg text-gray-900">
                                ⚡ EPEX Spot DE-LU
                            </h3>

                            <div className="text-xs text-gray-500">
                                Datenquelle: Energy Charts
                            </div>

                        </div>

                        <div className="flex items-center gap-2">

                            <div className="flex rounded-lg overflow-hidden border shadow-sm bg-white">

                                {[
                                    ["2d", "Heute + Morgen"],
                                    ["today", "Heute"],
                                    ["tomorrow", "Morgen"],
                                    ["5d", "5 Tage"],
                                ].map(([value, label]) => (

                                    <button
                                        key={value}
                                        onClick={() => setRange(value)}
                                        className={`
                                        px-3 py-1
                                        text-sm
                                        font-medium
                                        transition-colors
                                        ${range === value
                                                ? "bg-amber-500 text-white"
                                                : "text-gray-500 hover:bg-gray-50"
                                            }
                                    `}
                                    >
                                        {label}
                                    </button>

                                ))}

                            </div>

                            {["CSV", "XLSX", "PDF"].map(label => (
                                <button
                                    key={label}
                                    disabled
                                    className="
                                    px-3
                                    py-1
                                    text-sm
                                    rounded-lg
                                    text-white
                                    shadow-sm
                                    font-medium
                                    opacity-60
                                    cursor-not-allowed
                                "
                                    style={{
                                        backgroundColor: "#f59e0b"
                                    }}
                                    title="Kommt später 😉"
                                >
                                    {label}
                                </button>
                            ))}

                            {isZoomed && (
                                <button
                                    onClick={handleResetZoom}
                                    className="
                                        px-3
                                        py-1
                                        text-sm
                                        bg-amber-50
                                        hover:bg-amber-100
                                        text-amber-700
                                        border
                                        border-amber-200
                                        rounded-lg
                                        font-medium
                                        transition-colors
                                    "
                                >
                                    Reset
                                </button>
                            )}

                            <button
                                onClick={onClose}
                                className="text-gray-400 hover:text-gray-600 text-lg p-1 transition-colors"
                            >
                                ✕
                            </button>

                        </div>

                    </div>


                    {/* STATISTIK-KACHELN (Jetzt reaktiv gekoppelt an liveStats!) */}
                    {data && (
                        <div className="mt-4 flex justify-center">
                            <div className="grid grid-cols-4 gap-3 w-1/2 min-w-[500px]">

                                <div className="bg-white/70 rounded-lg p-2 border border-amber-100 shadow-sm">
                                    <div className="text-xs text-gray-500">Aktuell</div>
                                    <div className="font-semibold text-amber-600">
                                        {(data.current ?? 0).toFixed(2)} ct
                                    </div>
                                </div>

                                <div className="bg-white/70 rounded-lg p-2 border border-slate-100 shadow-sm">
                                    <div className="text-xs text-gray-500">Minimum (sichtbar)</div>
                                    <div className="font-semibold text-green-600">
                                        {liveStats.min.toFixed(2)} ct
                                    </div>
                                </div>

                                <div className="bg-white/70 rounded-lg p-2 border border-slate-100 shadow-sm">
                                    <div className="text-xs text-gray-500">Maximum (sichtbar)</div>
                                    <div className="font-semibold text-red-600">
                                        {liveStats.max.toFixed(2)} ct
                                    </div>
                                </div>

                                <div className="bg-white/70 rounded-lg p-2 border border-slate-100 shadow-sm">
                                    <div className="text-xs text-gray-500">Durchschnitt (sichtbar)</div>
                                    <div className="font-semibold text-gray-700">
                                        {liveStats.avg.toFixed(2)} ct
                                    </div>
                                </div>

                            </div>
                        </div>
                    )}
                </div>

                {/* CHART CONTAINER */}
                <div className="flex-1 p-4 relative min-h-0">
                    {data && (
                        <ReactECharts
                            ref={chartRef} // ✅ Verknüpft die Instanz für Zoom-Gesten
                            onEvents={onEvents} // ✅ Lauscht auf das Zoom-Event
                            notMerge={true}
                            lazyUpdate={false}
                            style={{ width: "100%", height: "100%" }}
                            option={{
                                tooltip: {
                                    trigger: "axis",
                                    formatter: (params) => {
                                        const p = params[0];
                                        if (!p) return "";
                                        return `
                                        <div>
                                            <div style="font-size:12px;color:#64748b;">${p.name}</div>
                                            <div style="color:#f59e0b;font-weight:600;">
                                                ${Number(p.value).toLocaleString(
                                            "de-DE",
                                            {
                                                minimumFractionDigits: 2,
                                                maximumFractionDigits: 2,
                                            }
                                        )} ct/kWh
                                            </div>
                                        </div>
                                    `;
                                    },
                                },
                                grid: {
                                    top: "8%",
                                    left: "4%",
                                    right: "4%",
                                    bottom: "15%", // Etwas mehr Platz nach unten für den Slider
                                    containLabel: true,
                                },
                                xAxis: {
                                    type: "category",
                                    data: chartData.xAxisData,
                                    boundaryGap: false,
                                    axisLine: { lineStyle: { color: '#cbd5e1' } },
                                    axisLabel: {
                                        color: "#64748b",

                                        interval: 15,

                                        formatter: (value) => {

                                            const parts = value.split(" ");

                                            return parts[1] || value;
                                        },
                                    },
                                },
                                yAxis: {
                                    type: "value",
                                    axisLine: { show: false },
                                    splitLine: { lineStyle: { color: '#f1f5f9' } },
                                    axisLabel: {
                                        color: '#64748b',
                                        formatter: "{value} ct",
                                    },
                                },
                                series: [
                                    {
                                        name: "Spotpreis",
                                        type: "line",
                                        smooth: true,
                                        showSymbol: false,
                                        data: chartData.seriesData,
                                        lineStyle: {
                                            color: "#f59e0b",
                                            width: 3,
                                        },
                                        areaStyle: {
                                            color: {
                                                type: "linear", x: 0, y: 0, x2: 0, y2: 1,
                                                colorStops: [
                                                    { offset: 0, color: "rgba(245,158,11,0.25)" },
                                                    { offset: 1, color: "rgba(245,158,11,0.00)" },
                                                ],
                                            },
                                        },
                                        markLine: {
                                            symbol: ["none", "none"],
                                            silent: true,

                                            data: [

                                                ...(data?.now_label
                                                    ? [{
                                                        xAxis: data.now_label,

                                                        label: {
                                                            formatter: "Jetzt",
                                                            position: "end",
                                                        },

                                                        lineStyle: {
                                                            color: "#dc2626",
                                                            width: 2,
                                                            type: "dashed",
                                                        },
                                                    }]
                                                    : []),

                                                ...(data?.tomorrow_label
                                                    ? [{
                                                        xAxis: data.tomorrow_label,

                                                        label: {
                                                            formatter: "Morgen",
                                                            position: "end",
                                                        },

                                                        lineStyle: {
                                                            color: "#64748b",
                                                            width: 2,
                                                        },
                                                    }]
                                                    : []),

                                                {
                                                    yAxis: liveStats.min,

                                                    label: {
                                                        formatter: `Min ${liveStats.min.toFixed(2)} ct`,
                                                    },

                                                    lineStyle: {
                                                        color: "#16a34a",
                                                        width: 1,
                                                    },
                                                },

                                                {
                                                    yAxis: liveStats.max,

                                                    label: {
                                                        formatter: `Max ${liveStats.max.toFixed(2)} ct`,
                                                    },

                                                    lineStyle: {
                                                        color: "#dc2626",
                                                        width: 1,
                                                    },
                                                },

                                                {
                                                    yAxis: liveStats.avg,

                                                    label: {
                                                        formatter: `Ø ${liveStats.avg.toFixed(2)} ct`,
                                                    },

                                                    lineStyle: {
                                                        color: "#64748b",
                                                        width: 1,
                                                        type: "dashed",
                                                    },
                                                },

                                            ],
                                        },
                                    },
                                ],
                                /* ✅ DATAZOOM BLOCK (Slider farblich angepasst und komplett geschlossen!) */
                                dataZoom: [
                                    {
                                        type: "inside",
                                        start: zoomRange.start,
                                        end: zoomRange.end,
                                    },
                                    {
                                        type: "slider",
                                        start: zoomRange.start,
                                        end: zoomRange.end,

                                        foregroundColor: "#f59e0b",
                                        borderColor: "#f1f5f9",

                                        textStyle: {
                                            color: "#64748b"
                                        }
                                    }
                                ]
                            }}

                        />
                    )}

                </div>

            </div>
        </div>
    );
}