/*
# pages/dashboard/tracking/TrackingPage.jsx
*/

import { useState } from "react";

import KPI from "../components/tracking/KPI";
import DaysFilter from "../components/tracking/DaysFilter";
import TrackingFunnel from "../components/tracking/FunnelChart";

import {
    useTrackingKPIs,
    useTrackingFunnel,
} from "../hooks/useTracking";


export default function TrackingDashboard() {

    const [days, setDays] = useState(7);

    const { data: kpis, isLoading: kpisLoading } = useTrackingKPIs(days);
    const { data: funnel, isLoading: funnelLoading } = useTrackingFunnel(days);

    if (kpisLoading || funnelLoading) {
        return <div className="p-6">Loading...</div>;
    }

    return (
        <div className="p-6 space-y-6">

            {/* Header */}
            <div className="flex justify-between items-center">
                <h1 className="text-xl font-semibold">Analytics</h1>
                <DaysFilter value={days} onChange={setDays} />
            </div>

            {/* KPI Grid */}
            <div className="grid grid-cols-3 gap-4">

                <KPI
                    label="DAU"
                    value={kpis?.dau}
                />

                <KPI
                    label="Landing → Signup"
                    value={`${kpis?.conversion_landing_signup}%`}
                />

                <KPI
                    label="Signup → Login"
                    value={`${kpis?.conversion_signup_login}%`}
                />

            </div>

            {/* Funnel */}
            <TrackingFunnel data={funnel} />

        </div>
    );
}
