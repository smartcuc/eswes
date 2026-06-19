/*
# src/PrivateApp.jsx
*/

import { useUser } from "./hooks/useUser";
import { useSettings } from "./hooks/useSettings";
import Onboarding from "./pages/Onboarding";
import AppShell from "./components/AppShell";
import { Navigate } from "react-router-dom";

export default function PrivateApp() {

    const { user, loading: userLoading } = useUser();
    const { settings, loading: settingsLoading } = useSettings();

    if (userLoading || settingsLoading) {
        return (
            <div className="min-h-screen flex items-center justify-center text-gray-400">
                Sharegy lädt…
            </div>
        );
    }


    if (!user) {
        return <Navigate to="/" replace />;
    }

    if (!settings) {
        return null;
    }

    if (settings.onboarding_step !== "done") {
        return <Onboarding />;
    }

    return <AppShell />;
}