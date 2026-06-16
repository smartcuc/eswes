/*
# src/pages/dashboard/DashboardTenant.jsx
*/

import DashboardLayout from "../../components/dashboard/DashboardLayout";
import KPI from "../../components/ui/KPI";
import Card from "../../components/ui/Card";
import Button from "../../components/ui/Button";

export default function DashboardTenant() {
    return (
        <DashboardLayout>

            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold">
                    Deine Community ⚡
                </h1>
                <p className="text-gray-500">
                    Energie teilen & gemeinsam profitieren
                </p>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-3 gap-4">
                <KPI label="Mitglieder" value="12" icon="👥" />
                <KPI label="Geteilte Energie" value="320" unit="kWh" icon="⚡" />
                <KPI label="Ersparnis" value="120" unit="€" icon="💰" />
            </div>

            {/* Activity */}
            <div className="space-y-2">
                <h2 className="text-lg font-semibold">Aktivität</h2>

                <Card>
                    <ul className="space-y-2 text-sm text-gray-600">
                        <li>✅ Max hat Energie eingespeist</li>
                        <li>✅ Neue Mitglieder beigetreten</li>
                    </ul>
                </Card>
            </div>

            {/* CTA */}
            <Card className="flex justify-between items-center">
                <span className="text-gray-600">
                    Lade neue Mitglieder ein
                </span>

                <Button>
                    Einladen
                </Button>
            </Card>

        </DashboardLayout>
    );
}

