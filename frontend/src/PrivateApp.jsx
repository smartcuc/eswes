/*
# src/PrivateApp.jsx
*/

import { useUser } from "./hooks/useUser";
import Onboarding from "./pages/Onboarding";
import Overview from "./pages/Overview";
import Settings from "./pages/Settings";
import { Routes, Route, Navigate } from "react-router-dom";

function AppShell() {
    return (
        <Routes>
            <Route path="/" element={<Overview mode="user" />} />
            <Route path="/dashboard" element={<Overview mode="user" />} />
            <Route path="/settings" element={<Settings />} />
        </Routes>
    );
}

function AppShellSkeleton({ loading, children }) {
    return (
        <div>
            {/* ✅ Header sofort da */}
            <div className="p-4 border-b">Sharegy</div>

            {/* ✅ Content */}
            {loading ? (
                <div className="p-6 text-gray-400">
                    Loading your data...
                </div>
            ) : (
                children
            )}
        </div>
    );
}

export default function PrivateApp() {

    const { user, loading, refreshUser } = useUser();

    // ✅ NICHT eingeloggt → raus
    if (!loading && !user) {
        return <Navigate to="/" replace />;
    }

    return (
        <AppShellSkeleton loading={loading}>
            {!loading && user && (
                user.onboarding_step !== "done"
                    ? <Onboarding refreshUser={refreshUser} />
                    : <AppShell />
            )}
        </AppShellSkeleton>
    );
}
