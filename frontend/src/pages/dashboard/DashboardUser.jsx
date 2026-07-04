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

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../api/client";

import LiveEnergySankey from "../../features/energy/components/LiveEnergySankey";


export default function DashboardUser() {

    const [openSetup, setOpenSetup] = useState(false);

    const energyQuery = useQuery({
        queryKey: ["energy-dashboard"],
        queryFn: () =>
            apiFetch("/api/energy/dashboard/me/"),
        refetchInterval: 5000,
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

                <h2 className="text-lg font-semibold mb-4">
                    Live Energiefluss
                </h2>

                <LiveEnergySankey
                    data={energyQuery.data?.sankey}
                />

            </Card>

        </DashboardLayout>
    );
}

