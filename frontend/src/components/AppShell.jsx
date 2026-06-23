/*
# components/AppShell.jsx
*/

import { useUser } from "../hooks/useUser";
import Dashboard from "../pages/dashboard/Dashboard";
import OverviewPage from "../pages/dashboard/overview/OverviewPage";
import Settings from "../pages/Settings";
import { Routes, Route, Navigate } from "react-router-dom";
import EnergyDashboard from "../features/energy/EnergyDashboard";

import AppHeader from "../components/AppHeader";

export default function AppShell() {

    const { user, loading } = useUser();

    if (loading) {
        return <div className="p-6">Loading...</div>;
    }

    // ❗ nicht eingeloggt → zurück zu landing
    if (!user) {
        return <Navigate to="/" replace />;
    }


    return (

        <div className="flex flex-col h-screen">

            {/* ✅ HEADER → enthält UserMenu */}
            <AppHeader />

            {/* ✅ CONTENT */}
            <div className="flex-1 overflow-auto">

                <Routes>
                    {/* ✅ Default */}
                    <Route index element={<Navigate to="dashboard" replace />} />

                    {/* ✅ bestehendes User-Dashboard */}
                    <Route path="dashboard" element={<Dashboard user={user} />} />

                    {/* ✅ NEU – Overview */}
                    <Route path="overview" element={<OverviewPage />} />

                    {/* ⚡ ENERGY DASHBOARD */}
                    <Route path="energy" element={<EnergyDashboard />} />

                    <Route path="settings" element={<Settings />} />

                    {/* ✅ Fallback */}
                    <Route path="*" element={<Navigate to="dashboard" />} />
                </Routes>

            </div>

        </div>
    );
}

// {isRefreshing && <span className="text-xs text-gray-400">Syncing...</span>} muss noch iregenwo in
// der UI eingebaut werden