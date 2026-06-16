/*
# src/pages/dashboard/DashboardHybrid.jsx
*/

import DashboardLayout from "../../components/dashboard/DashboardLayout";
import KPI from "../../components/ui/KPI";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

export default function DashboardHybrid() {
    return (
        <DashboardLayout>

            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">
                    Energie & Community ⚡
                </h1>
                <p className="text-gray-500">
                    Dein persönliches System + deine Community
                </p>
            </div>

            {/* PERSONAL */}
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">Deine Energie</h2>

                <div className="grid grid-cols-3 gap-4">
                    <KPI label="Verbrauch" value="12" unit="kWh" icon="⚡" />
                    <KPI label="Produktion" value="8" unit="kWh" icon="☀️" />
                    <KPI label="Kosten" value="4.20" unit="€" icon="💰" />
                </div>
            </div>

            {/* COMMUNITY */}
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">Community</h2>

                <div className="grid grid-cols-3 gap-4">
                    <KPI label="Mitglieder" value="12" icon="👥" />
                    <KPI label="Geteilt" value="320" unit="kWh" icon="⚡" />
                    <KPI label="Ersparnis" value="120" unit="€" icon="💰" />
                </div>
            </div>

            {/* CTA */}
            <Card className="flex justify-between items-center">
                <span className="text-gray-600">
                    Verwalte deine Energie & Community
                </span>

                <Button>
                    Verwalten
                </Button>
            </Card>

        </DashboardLayout>
    );
}
