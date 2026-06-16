/*
# src/pages/Settings.jsx
*/

import AppLayout from "../components/AppLayout";
import DashboardLayout from "../components/dashboard/DashboardLayout";
import Card from "../components/ui/Card";
import Button from "../components/ui/Button";
import { useUser } from "../hooks/useUser";

export default function Settings() {

    async function changeLanguage(lang) {
        const { user, setUser } = useUser();

        await fetch("/api/user-language/", {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ language: lang }),
        });

        // ✅ sofort UI update (kein fetch nötig)
        setUser(prev => ({
            ...prev,
            language: lang
        }));
    }

    return (
        <AppLayout>
            <DashboardLayout>

                {/* HEADER */}
                <div className="mb-10">
                    <h1 className="text-2xl font-semibold">
                        Einstellungen
                    </h1>
                    <p className="text-gray-500">
                        Deine persönlichen Einstellungen
                    </p>
                </div>

                {/* USER INFO */}
                <Card>
                    <h2 className="font-medium mb-4">
                        Account
                    </h2>

                    <div className="text-sm text-gray-600">
                        {user?.email}
                    </div>
                </Card>

                {/* LANGUAGE */}
                <div className="mt-10">
                    <Card>
                        <h2 className="font-medium mb-4">
                            Sprache
                        </h2>

                        <div className="flex gap-3">
                            <Button onClick={() => changeLanguage("de")}>
                                Deutsch
                            </Button>

                            <Button
                                variant="secondary"
                                onClick={() => changeLanguage("en")}
                            >
                                English
                            </Button>
                        </div>
                    </Card>
                </div>

                {/* FUTURE SECTION */}
                <div className="mt-10">
                    <Card>
                        <h2 className="font-medium mb-4">
                            Anzeige & Theme
                        </h2>

                        <p className="text-sm text-gray-500">
                            Anpassbare Farben und Themes folgen in Kürze.
                        </p>
                    </Card>
                </div>

            </DashboardLayout>
        </AppLayout>
    );
}
