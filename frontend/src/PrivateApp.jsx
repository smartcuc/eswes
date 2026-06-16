/*
# src/PrivateApp.jsx
*/

import { useUser } from "./hooks/useUser";
import Onboarding from "./pages/Onboarding";
import AppShell from "./components/AppShell";
import { Navigate } from "react-router-dom";

export default function PrivateApp() {
    const { user, loading, refreshUser } = useUser();

    // ✅ Warten bis User geladen ist (CRITICAL!)
    if (loading) {
        return (
            <div className="p-6 text-gray-400">
                Loading your data...
            </div>
        );
    }

    // ✅ Nicht eingeloggt → raus
    if (!user) {
        return <Navigate to="/" replace />;
    }

    // ✅ Onboarding entscheidet ALLES
    if (user.onboarding_step !== "done") {
        return (
            <Onboarding
                user={user}
                refreshUser={refreshUser}
            />
        );
    }

    // ✅ Fertig → App
    return <AppShell />;
}
