/*
# src/pages/dashboard/DashboardUser.jsx
*/

import DashboardLayout from "../../components/dashboard/DashboardLayout";
import UnconfiguredDevicesBanner from "../../components/dashboard/UnconfiguredDevicesBanner";
import DeviceSetupModal from "../../components/device/DeviceSetupModal";
import KPI from "../../components/ui/KPI";
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
                    Dein Energie Dashboard ⚡
                </h1>
                <p className="text-gray-500">
                    Dein persönlicher Energieüberblick
                </p>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-3 gap-4">
                <KPI label="Verbrauch" value="12" unit="kWh" icon="⚡" />
                <KPI label="Produktion" value="8" unit="kWh" icon="☀️" />
                <KPI label="Kosten" value="4.20" unit="€" icon="💰" />
            </div>

            {/* Chart */}
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">Verlauf</h2>

                <Card>
                    <div className="h-40 flex items-center justify-center text-gray-400">
                        📈 Energiechart (kommt später)
                    </div>
                </Card>
            </div>

            {/* CTA */}
            <Card className="flex justify-between items-center">
                <span className="text-gray-600">
                    Starte mit deinem ersten Energiegerät
                </span>
            </Card>

            <Card>

                <div className="flex items-center justify-between mb-4">

                    <h2 className="text-lg font-semibold">
                        Live Energiefluss
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

                <LiveEnergySankey
                    data={energyQuery.data?.sankey}
                />

            </Card>

        </DashboardLayout>
    );
}

