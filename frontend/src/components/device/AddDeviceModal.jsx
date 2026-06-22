/*
# src/components/device/AddDeviceModal.jsx
*/

import { useEffect, useState } from "react";
import { useCreateDevice } from "../../hooks/useCreateDevice";
import { useDeviceStatus } from "../../hooks/useDevices";

export default function AddDeviceModal({ open, onClose }) {

    const [step, setStep] = useState(1);
    const [connection, setConnection] = useState(null);
    const [name, setName] = useState("");
    const [device, setDevice] = useState(null);

    const createDevice = useCreateDevice();

    if (!open) return null;

    function next() {
        setStep((s) => s + 1);
    }

    function back() {
        setStep((s) => Math.max(1, s - 1));
    }

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">

            <div className="bg-white text-gray-800 p-6 rounded-xl w-full max-w-md relative shadow-xl">

                {/* Step Indicator */}
                <div className="text-sm text-gray-400 mb-4">
                    Schritt {step} von 4
                </div>

                {/* Steps */}
                {step === 1 && (
                    <StepConnection
                        onSelect={(type) => {
                            setConnection(type);
                            next();
                        }}
                    />
                )}

                {step === 2 && (
                    <StepName
                        name={name}
                        setName={setName}
                        onNext={async () => {

                            const identifier = name.toLowerCase().replace(/\s+/g, "_");

                            try {
                                const result = await createDevice.mutateAsync({
                                    identifier
                                });

                                setDevice(result);
                                next();

                            }
                            catch (err) {
                                console.error("Device creation failed", err);

                                if (err.type === "validation") {
                                    console.error("VALIDATION ERRORS:", err.data);
                                    alert(JSON.stringify(err.data));
                                } else {
                                    alert("Fehler beim Erstellen des Geräts");
                                }
                            }

                        }}
                        onBack={back}
                    />
                )}


                {step === 3 && device && (
                    <StepConfig
                        device={device}
                        onNext={next}
                        onBack={back}
                    />
                )}


                {step === 4 && (
                    <StepWaiting device={device} onClose={onClose} />
                )}

                {/* Close */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-gray-400"
                >
                    ✕
                </button>

            </div>
        </div>
    );
}


/* ------------------ STEP 1 ------------------ */

function StepConnection({ onSelect }) {

    return (
        <div>
            <h2 className="text-lg font-semibold mb-4">
                Wie möchtest du dein Gerät verbinden?
            </h2>

            <div className="space-y-2">
                <button onClick={() => onSelect("iobroker")} className="w-full p-3 bg-gray-100 rounded hover:bg-gray-200">
                    ioBroker
                </button>

                <button onClick={() => onSelect("ha")} className="w-full p-3 bg-gray-100 rounded hover:bg-gray-200">
                    Home Assistant
                </button>

                <button onClick={() => onSelect("mqtt")} className="w-full p-3 bg-gray-100 rounded hover:bg-gray-200">
                    MQTT (Advanced)
                </button>
            </div>
        </div>
    );
}


/* ------------------ STEP 2 ------------------ */

function StepName({ name, setName, onNext, onBack }) {

    return (
        <div>
            <h2 className="text-lg font-semibold mb-4">
                Gib deinem Gerät einen Namen
            </h2>

            <input
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="z.B. Wärmepumpe"
                className="w-full p-2 border rounded mb-4"
            />

            <div className="flex justify-between">
                <button onClick={onBack} className="text-gray-500">
                    Zurück
                </button>

                <button
                    onClick={onNext}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg"
                    disabled={!name}
                >
                    Weiter
                </button>
            </div>
        </div>
    );
}


/* ------------------ STEP 3 ------------------ */

function StepConfig({ device, onNext, onBack }) {

    const token = device?.mqtt_token;

    const topic = `home/${token}/device/${device.identifier}`;

    return (
        <div>
            <h2 className="text-lg font-semibold mb-4">
                Deine Verbindung
            </h2>


            <div className="bg-gray-100 p-3 rounded text-sm mb-4">

                <div><strong>Host:</strong> {device.mqtt_host}</div>
                <div><strong>Port:</strong> {device.mqtt_port}</div>
                <div><strong>Username:</strong> {device.mqtt_username}</div>
                <div><strong>Password:</strong> {device.mqtt_password}</div>

                <div className="mt-3 text-gray-500">Topic:</div>
                <div className="text-indigo-600 break-all">
                    {topic}
                </div>
            </div>

            <div className="flex justify-between">
                <button onClick={onBack} className="text-gray-500">
                    Zurück
                </button>

                <button
                    onClick={onNext}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg"
                >
                    Fertig
                </button>
            </div>
        </div>
    );
}


/* ------------------ STEP 4 ------------------ */

function StepWaiting({ device, onClose }) {

    const { data: devices } = useDeviceStatus();

    const [connected, setConnected] = useState(false);
    const [timeoutReached, setTimeoutReached] = useState(false);

    // ✅ Device Status ermitteln
    const deviceStatus = devices?.find(
        (d) => d.identifier === device?.identifier
    );

    // ✅ Erfolg erkennen (SAUBER via useEffect!)
    useEffect(() => {
        if (deviceStatus?.status === "online") {
            setConnected(true);
        }
    }, [deviceStatus]);

    // ✅ Timeout (einmal starten)
    useEffect(() => {
        const timer = setTimeout(() => {
            setTimeoutReached(true);
        }, 30000);

        return () => clearTimeout(timer);
    }, []);

    // =====================================================
    // ✅ SUCCESS STATE
    // =====================================================
    if (connected) {
        return (
            <div className="text-center">
                <h2 className="text-lg font-semibold mb-4">
                    ✅ Gerät verbunden!
                </h2>

                <div className="text-gray-500 mb-4">
                    Dein Gerät sendet bereits Daten.
                </div>

                <button
                    onClick={onClose}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg"
                >
                    Zum Dashboard
                </button>
            </div>
        );
    }

    // =====================================================
    // ✅ TIMEOUT STATE
    // =====================================================
    if (timeoutReached && deviceStatus?.status !== "online") {
        return (
            <div className="text-center">
                <h2 className="text-lg font-semibold mb-4">
                    ⏳ Noch keine Daten empfangen
                </h2>

                <div className="text-gray-500 mb-4">
                    Prüfe bitte MQTT‑Verbindung oder Gerät.
                </div>

                <button
                    onClick={onClose}
                    className="bg-indigo-600 text-white px-4 py-2 rounded-lg"
                >
                    Schließen
                </button>
            </div>
        );
    }

    // =====================================================
    // ✅ WAITING STATE
    // =====================================================
    return (
        <div className="text-center">
            <h2 className="text-lg font-semibold mb-4">
                Warte auf erste Daten…
            </h2>

            <div className="text-gray-500 mb-4">
                Sobald dein Gerät sendet, verbinden wir es automatisch.
            </div>

            <div className="animate-pulse text-indigo-600">
                ⏳ Verbinde…
            </div>

            {/* ✅ kleiner UX Boost */}
            {deviceStatus?.status === "offline" && (
                <div className="mt-3 text-sm text-gray-400">
                    Gerät erkannt, aber noch nicht aktiv…
                </div>
            )}
        </div>
    );
}
