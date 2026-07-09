/*
# src/pages/dashboard/DashboardUser.jsx
*/

import { useState } from "react";
import DashboardLayout from "../../components/dashboard/DashboardLayout";
import UnconfiguredDevicesBanner from "../../components/dashboard/UnconfiguredDevicesBanner";
import DeviceSetupModal from "../../components/device/DeviceSetupModal";
import EnergyChartModal from "../../features/energy/components/EnergyChartModal";
import KPI from "../../components/ui/KPI";
import KPISparklineECharts from "../../components/ui/KPISparklineECharts";
import Card from "../../components/ui/Card";

//import Button from "../../components/ui/Button";

import useUserPreference from "../../hooks/useUserPreference";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../api/client";

import LiveEnergySankey from "../../features/energy/components/LiveEnergySankey";
//import LiveEnergySankeyECharts from "../../features/energy/components/LiveEnergySankeyECharts";


export default function DashboardUser() {

    const queryClient = useQueryClient();
    const [openSetup, setOpenSetup] = useState(false);

    const {
        value: settings,
        setValue: saveSettings,
    } = useUserPreference("sankey");

    const showFloors = settings.showFloors ?? true;
    const showRooms = settings.showRooms ?? true;

    const energyQuery = useQuery({
        queryKey: [
            "energy-dashboard",
            showFloors,
            showRooms,
        ],
        queryFn: () => apiFetch("/api/energy/dashboard/me/"),
        refetchInterval: 3000, // ✅ VERY IMPORTANT
        refetchIntervalInBackground: true,
    });

    const kpis = energyQuery.data?.kpis || {};
    const charts = energyQuery.data?.charts || {};
    const [activeSystemChart, setActiveSystemChart] = useState(null);

    return (
        <DashboardLayout>

            {/* Header */}

            <div className="p-6">

                {/* <UnconfiguredDevicesBanner /> */}
                <UnconfiguredDevicesBanner onOpen={() => setOpenSetup(true)} />
                <DeviceSetupModal
                    open={openSetup}
                    onClose={() => setOpenSetup(false)}
                />

            </div>

            <div>
                <h1 className="text-2xl font-bold">
                    Deine Energiezentrale ⚡
                </h1>
                <p className="text-gray-500">
                    Alles Wichtige auf einen Blick.
                </p>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">

                <KPI
                    label="Aktuelle Last"
                    value={kpis.load ?? "--"}
                    unit="W"
                    icon="⚡"
                    chart={
                        <KPISparklineECharts
                            color="#2563eb"
                            values={charts.load || []}
                        />
                    }
                />

                <KPI
                    label="Erzeugung"
                    value={kpis.pv ?? "--"}
                    unit="W"
                    icon="☀️"
                    chart={
                        <KPISparklineECharts
                            color="#f59e0b"
                            values={charts.pv || []}
                        />
                    }
                />

                {/* ✅ KACHEL 1: NETZ */}
                <div
                    onClick={() => setActiveSystemChart({ metricKey: "grid", displayName: "Netzanschluss", unit: "W" })}
                    className="cursor-pointer hover:opacity-90 transition-opacity"
                >

                    <KPI
                        label="Netz"
                        value={kpis.grid ?? "--"}
                        unit="W"
                        icon="🔌"
                        chart={
                            <KPISparklineECharts
                                color="#10b981"
                                values={charts.grid || []}
                            />

                        }
                    />
                </div>

                <KPI
                    label="Heute"
                    value={
                        kpis.today?.toLocaleString("de-DE", {
                            minimumFractionDigits: 2,
                            maximumFractionDigits: 2,
                        })
                    }
                    unit="kWh"
                    icon="📈"
                    chart={
                        <KPISparklineECharts
                            color="#8b5cf6"
                            values={charts.today || []}
                        />
                    }
                />

            </div>

            {/* Sankey Chart */}
            <Card>

                <div className="flex items-center justify-between mb-4">

                    <h2 className="text-lg font-semibold">
                        Energieübersicht
                    </h2>

                    <div className="flex gap-2">

                        <button
                            title="Nach Etagen gruppieren"
                            onClick={async () => {
                                await saveSettings({
                                    ...settings,
                                    showFloors: !showFloors,
                                });

                                energyQuery.refetch();
                            }}

                            className={`
                    px-2.5 py-1
                    rounded-full
                    text-xs
                    border
                    flex items-center gap-1
                    transition
                    ${showFloors
                                    ? "bg-indigo-600 text-white border-indigo-600"
                                    : "bg-white hover:bg-gray-50 border-gray-200"}
                `}
                        >
                            🏢 Etagen
                        </button>

                        <button
                            title="Nach Räumen gruppieren"
                            onClick={async () => {
                                await saveSettings({
                                    ...settings,
                                    showRooms: !showRooms,
                                });

                                queryClient.invalidateQueries({
                                    queryKey: ["energy-dashboard"],
                                })

                            }}

                            className={`
                    px-2.5 py-1
                    rounded-full
                    text-xs
                    border
                    flex items-center gap-1
                    transition
                    ${showRooms
                                    ? "bg-indigo-600 text-white border-indigo-600"
                                    : "bg-white hover:bg-gray-50 border-gray-200"}
                `}
                        >
                            🚪 Räume
                        </button>

                    </div>

                </div>

                {energyQuery.data?.ready ? (

                    <LiveEnergySankey
                        data={energyQuery.data?.sankey}
                    />

                ) : (

                    <div className="h-40 flex flex-col items-center justify-center text-center text-gray-400 space-y-1">
                        <p className="text-gray-500 font-medium">Willkommen bei Sharegy 👋</p>
                        <p>📈 Dein Energiechart kommt, sobald wir uns besser kennengelernt haben.</p>
                    </div>

                )}

            </Card>

            {/* 💡 EMS SYSTEM CHART MODAL */}
            {activeSystemChart && (
                <EnergyChartModal
                    metricKey={activeSystemChart.metricKey}
                    displayName={activeSystemChart.displayName}
                    unit={activeSystemChart.unit}
                    onClose={() => setActiveSystemChart(null)}
                />
            )}

        </DashboardLayout>
    );
}

