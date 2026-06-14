/*
# components/AppShell.jsx
*/

import { useUser } from "../hooks/useUser";
import Dashboard from "../pages/Dashboard";
import Settings from "../pages/Settings";
import { Routes, Route, Navigate } from "react-router-dom";

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
        <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/settings" element={<Settings />} />
        </Routes>
    );
}

// {isRefreshing && <span className="text-xs text-gray-400">Syncing...</span>} muss noch iregenwo in
// der UI eingebaut werden