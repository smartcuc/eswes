/*
# src/pages/dashboard/DashboardUser.jsx
*/

import DashboardLayout from "../../components/dashboard/DashboardLayout";
import UnconfiguredDevicesBanner from "../../components/dashboard/UnconfiguredDevicesBanner";
import DeviceSetupModal from "../../components/device/DeviceSetupModal";
import KPI from "../../components/ui/KPI";
import KPISparklineECharts from "../../components/ui/KPISparklineECharts";
import Card from "../../components/ui/Card";

import Button from "../../components/ui/Button";

import { useState } from "react";
import useUserPreference from "../../hooks/useUserPreference";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { apiFetch } from "../../api/client";

import LiveEnergySankey from "../../features/energy/components/LiveEnergySankey";
import LiveEnergySankeyECharts from "../../features/energy/components/LiveEnergySankeyECharts";


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
                            values={[2, 3, 2.5, 4, 5, 4, 6, 5]}
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
                            values={[0, 1, 2, 4, 5, 6, 5, 4]}
                        />
                    }
                />

                <KPI
                    label="Netz"
                    value={kpis.grid ?? "--"}
                    unit="W"
                    icon="🔌"
                    chart={
                        <KPISparklineECharts
                            color="#10b981"
                            values={[4, 3, 3.5, 2, 2.5, 1, 0.5, 0]}
                        />
                    }
                />

                <KPI
                    label="Heute"
                    value="--"
                    unit="kWh"
                    icon="📈"
                    chart={
                        <KPISparklineECharts
                            color="#8b5cf6"
                            values={[1, 2, 3, 4, 5, 7, 9, 12]}
                        />
                    }
                />

            </div>

            {/* Chart */}
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">Verlauf</h2>

                <Card>
                    <div className="h-40 flex items-center justify-center text-gray-400">
                        📈 Energiechart kommt sobald wir uns besser kennengelernt haben
                    </div>
                </Card>
            </div>

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

                    <div
                        className="
                            h-80
                            flex
                            items-center
                            justify-center
                            text-gray-400
        "
                    >
                        👋 Willkommen bei Sharegy
                    </div>

                )}

            </Card>

        </DashboardLayout>
    );
}

