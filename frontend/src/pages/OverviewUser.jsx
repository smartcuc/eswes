/*
# src/pages/OverviewUser.jsx
*/

import { useState, useEffect } from "react";
import AppLayout from "../components/AppLayout";
import OverviewLayout from "../components/overview/OverviewLayout";
import EnergyFlow from "../components/EnergyFlow";
import Card from "../components/ui/Card";

// ✅ Komponenten
import DeviceDiscoveryBanner from "../components/DeviceDiscoveryBanner";
import DeviceSetupModal from "../components/DeviceSetupModal";

// ✅ DEV SWITCH (wichtig!)
const USE_FAKE = true;

export default function OverviewUser() {

    // ✅ STATE
    const [data, setData] = useState(null);
    const [modalOpen, setModalOpen] = useState(false);

    // ✅ DATA FETCH

    useEffect(() => {

        const url = USE_FAKE
            ? "/api/energy/fake-dashboard/"
            : "/api/energy/dashboard/me/";

        const load = () => {
            fetch(url)
                .then((res) => res.json())
                .then(setData)
                .catch(() => setData(null));
        };
        load(); // sofort laden

        const interval = setInterval(load, 2000); // alle 2s neu

        return () => clearInterval(interval);

    }, []);


    // ✅ LOGIK
    const hasFlow = !!data?.flow;

    return (
        <AppLayout>

            <OverviewLayout>

                {/* ✅ HEADER */}
                <div className="mb-10">
                    <h1 className="text-2xl font-semibold">
                        Dashboard
                    </h1>
                    <p className="text-gray-500">
                        Dein persönlicher Energieüberblick
                    </p>
                </div>

                {/* ✅ DEVICE BANNER */}
                {data && (
                    <DeviceDiscoveryBanner
                        devices={data.devices}
                        onOpen={() => setModalOpen(true)}
                    />
                )}

                {/* ✅ EMPTY STATE (nur initial / loading fallback) */}
                {!data && (
                    <>
                        <Card>
                            <div className="text-center">

                                <h2 className="text-lg font-medium mb-2">
                                    Dashboard bereit
                                </h2>

                                <p className="text-gray-500 mb-4">
                                    Aktuell sind noch keine Daten verfügbar.
                                </p>

                                <p className="text-sm text-gray-400">
                                    Vorschau unten.
                                </p>

                            </div>
                        </Card>

                        {/* PREVIEW */}
                        <div className="mt-10">
                            <Card>

                                <h3 className="font-medium mb-2">
                                    Energiefluss Vorschau
                                </h3>

                                <EnergyFlow />

                            </Card>
                        </div>
                    </>
                )}

                {/* ✅ DATEN DA, ABER KEIN FLOW */}
                {data && !hasFlow && (
                    <Card className="mt-10">
                        <div className="text-center">

                            <h2 className="text-lg font-medium mb-2">
                                Noch keine Energiedaten
                            </h2>

                            <p className="text-gray-500 mb-6">
                                Starte mit Demo-Daten oder verbinde ein Gerät.
                            </p>

                            <div className="flex justify-center gap-4">

                                {/* ✅ DEMO BUTTON */}
                                <button
                                    onClick={async () => {
                                        if (USE_FAKE) {
                                            window.location.reload();
                                        } else {
                                            await fetch("/api/energy/demo/start/", {
                                                method: "POST",
                                            });
                                            window.location.reload();
                                        }
                                    }}
                                    className="px-4 py-2 bg-indigo-500 text-white rounded"
                                >
                                    ✨ Demo starten
                                </button>

                                <button className="px-4 py-2 bg-yellow-100 rounded">
                                    🔌 Gerät verbinden
                                </button>

                            </div>

                        </div>
                    </Card>
                )}

                {/* ✅ FLOW ANZEIGE */}
                {data && hasFlow && (
                    <div className="mt-10">
                        <Card>

                            <h3 className="font-medium mb-2">
                                Dein Energiefluss
                            </h3>

                            <EnergyFlow data={data} />

                        </Card>
                    </div>
                )}

            </OverviewLayout>

            {/* ✅ MODAL */}
            {modalOpen && data && (
                <DeviceSetupModal
                    devices={data.devices?.unconfigured || []}
                    onClose={() => setModalOpen(false)}
                    onSaved={() => {
                        setModalOpen(false);
                        window.location.reload();
                    }}
                />
            )}

        </AppLayout>
    );
}
