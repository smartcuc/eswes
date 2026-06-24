/*
# src/components/device/AddDeviceModal.jsx
*/

import { useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";
import { useCreateDevice } from "../../hooks/useCreateDevice";
import { useDeviceStatus } from "../../hooks/useDevices";

/* =========================================================
   HELPERS
========================================================= */

function safeCopy(text, setCopiedKey, key) {
    if (navigator.clipboard) {
        navigator.clipboard.writeText(text);
        setCopiedKey(key);
        setTimeout(() => setCopiedKey(null), 1500);
    } else {
        alert("Copy wird nicht unterstützt");
    }
}

function Row({ label, value, copyKey, copiedKey, setCopiedKey }) {
    return (
        <div className="flex justify-between items-center mt-1">
            <span><strong>{label}:</strong> {value}</span>

            <button
                onClick={() => safeCopy(value, setCopiedKey, copyKey)}
                className="text-xs bg-gray-200 px-2 py-1 rounded"
            >
                {copiedKey === copyKey ? "✅" : "Copy"}
            </button>
        </div>
    );
}


/* =========================================================
   MAIN MODAL
========================================================= */

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
        if (!createDevice.isLoading) {
            setStep((s) => Math.max(1, s - 1));
        }
    }

    return (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50">
            <div className="bg-white text-gray-800 p-6 rounded-xl w-full max-w-md relative shadow-xl">

                <div className="text-sm text-gray-400 mb-4">
                    Schritt {step} von 4
                </div>

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
                        loading={createDevice.isLoading}
                        onNext={async () => {

                            const identifier = name.toLowerCase().replace(/\s+/g, "_");

                            try {
                                const result = await createDevice.mutateAsync({ identifier });
                                setDevice(result);
                                next();
                            } catch {
                                alert("Fehler beim Erstellen des Geräts");
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


/* =========================================================
   STEP 1
========================================================= */

function StepConnection({ onSelect }) {
    return (
        <div>
            <h2 className="text-lg font-semibold mb-4">
                Wie verbinden?
            </h2>

            <div className="space-y-2">
                <button onClick={() => onSelect("iobroker")} className="w-full p-3 bg-gray-100 rounded">
                    ioBroker
                </button>

                <button onClick={() => onSelect("ha")} className="w-full p-3 bg-gray-100 rounded">
                    Home Assistant
                </button>

                <button onClick={() => onSelect("mqtt")} className="w-full p-3 bg-gray-100 rounded">
                    MQTT
                </button>
            </div>
        </div>
    );
}


/* =========================================================
   STEP 2
========================================================= */

function StepName({ name, setName, onNext, onBack, loading }) {

    function submit(e) {
        e.preventDefault();
        if (name && !loading) onNext();
    }

    return (
        <form onSubmit={submit}>
            <h2 className="text-lg font-semibold mb-4">
                Gerätenamen
            </h2>

            <input
                autoFocus
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="z.B. Wärmepumpe"
                className="w-full p-2 border rounded mb-4"
            />

            <div className="flex justify-between">
                <button type="button" onClick={onBack} disabled={loading}>
                    Zurück
                </button>

                <button
                    type="submit"
                    disabled={!name || loading}
                    className="bg-indigo-600 text-white px-4 py-2 rounded"
                >
                    {loading ? "Erstelle..." : "Weiter"}
                </button>
            </div>
        </form>
    );
}


/* =========================================================
   STEP 3 (CONFIG + VERIFY)
========================================================= */

function StepConfig({ device, onNext, onBack }) {

    const [copiedKey, setCopiedKey] = useState(null);
    const [showQR, setShowQR] = useState(false);
    const [autoAdvanced, setAutoAdvanced] = useState(false);
    const [sendingMail, setSendingMail] = useState(false);

    const { data: devices, refetch } = useDeviceStatus();

    const topic = `home/${device.mqtt_token}/device/${device.identifier}`;

    const status = devices?.find(d => d.identifier === device.identifier);

    const connected =
        status?.status === "online" ||
        status?.status === "stale";

    const waiting = !connected;

    const [email, setEmail] = useState("");
    const [magicLoading, setMagicLoading] = useState(false);
    const [magicStatus, setMagicStatus] = useState(null);

    // ✅ AUTO SKIP (nur einmal)
    useEffect(() => {
        if (connected && !autoAdvanced) {
            setAutoAdvanced(true);

            const t = setTimeout(() => {
                onNext();
            }, 800);

            return () => clearTimeout(t);
        }
    }, [connected, autoAdvanced, onNext]);

    return (
        <div>

            <h2 className="text-lg font-semibold mb-4">
                Verbindung
            </h2>

            {/* ✅ QR CODE */}
            <div className="bg-white p-3 rounded border text-center mb-4">

                <div className="text-sm text-gray-500 mb-2">
                    QR Code
                </div>

                <div
                    onClick={() => setShowQR(true)}
                    className="cursor-pointer flex justify-center"
                >
                    <QRCodeSVG
                        value={JSON.stringify({
                            host: device.mqtt_host,
                            port: device.mqtt_port,
                            username: device.mqtt_username,
                            password: device.mqtt_password,
                            topic: topic
                        })}
                        size={140}
                    />
                </div>

                <div className="text-xs text-gray-400 mt-2">
                    klicken zum Vergrößern
                </div>
            </div>

            {/* ✅ CONFIG */}
            <div className="bg-gray-100 p-3 rounded text-sm mb-4">

                <Row label="Host" value={device.mqtt_host} copyKey="host" copiedKey={copiedKey} setCopiedKey={setCopiedKey} />
                <Row label="Port" value={device.mqtt_port} copyKey="port" copiedKey={copiedKey} setCopiedKey={setCopiedKey} />
                <Row label="User" value={device.mqtt_username} copyKey="user" copiedKey={copiedKey} setCopiedKey={setCopiedKey} />
                <Row label="Pass" value={device.mqtt_password} copyKey="pass" copiedKey={copiedKey} setCopiedKey={setCopiedKey} />

                <div className="mt-3 text-gray-500">Topic</div>

                <div className="flex justify-between items-center">
                    <span className="text-indigo-600 break-all">{topic}</span>

                    <button
                        onClick={() => safeCopy(topic, setCopiedKey, "topic")}
                        className="text-xs bg-gray-200 px-2 py-1 rounded"
                    >
                        {copiedKey === "topic" ? "✅" : "Copy"}
                    </button>
                </div>
            </div>

            {/* ✅ COPY ALL */}
            <button
                onClick={() => {
                    const text = `MQTT Setup:

Host: ${device.mqtt_host}
Port: ${device.mqtt_port}
User: ${device.mqtt_username}
Pass: ${device.mqtt_password}

Topic:
${topic}`;

                    safeCopy(text, setCopiedKey, "all");
                }}
                className="mb-4 text-sm bg-gray-200 px-3 py-2 rounded"
            >
                {copiedKey === "all" ? "✅ Alles kopiert" : "📋 Alles kopieren"}
            </button>

            {/* ✅ STATUS / PROGRESS */}
            <div className="mb-4">

                {waiting && (
                    <div className="text-indigo-600 text-sm flex items-center gap-2">
                        <span className="animate-pulse">⏳</span>
                        Verbindung wird geprüft…
                    </div>
                )}

                {connected && (
                    <div className="text-green-600 text-sm">
                        ✅ Verbindung erkannt
                    </div>
                )}

            </div>

            {/* ✅ MAIL (Backend) */}
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="E-Mail (optional überschreiben)"
                className="w-full mb-3 p-2 border rounded"
            />
            <button
                onClick={async () => {

                    try {
                        setMagicLoading(true);
                        setMagicStatus(null);

                        const text = `MQTT Setup:

Host: ${device.mqtt_host}
Port: ${device.mqtt_port}
User: ${device.mqtt_username}
Pass: ${device.mqtt_password}

Topic:
${topic}`;

                        // ✅ 1. Copy ALL
                        if (navigator.clipboard) {
                            await navigator.clipboard.writeText(text);
                        }

                        // ✅ 2. Backend Mail
                        await fetch("/api/devices/send-config/", {
                            method: "POST",
                            headers: {
                                "Content-Type": "application/json",
                                Authorization: `Bearer ${localStorage.getItem("token")}`
                            },
                            body: JSON.stringify({
                                device,
                                email: email || null
                            }),
                        });

                        setMagicStatus("success");

                    } catch (e) {
                        setMagicStatus("error");
                    } finally {
                        setMagicLoading(false);
                    }

                }}
                disabled={magicLoading}
                className="mb-4 w-full bg-indigo-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
            >
                {magicLoading
                    ? "Sende & kopiere..."
                    : "✨ Setup senden + kopieren"}
            </button>

            {magicStatus === "success" && (
                <div className="text-green-600 text-sm mb-3">
                    ✅ Mail gesendet & Daten kopiert
                </div>
            )}

            {magicStatus === "error" && (
                <div className="text-red-600 text-sm mb-3">
                    ❌ Fehler beim Senden
                </div>
            )}

            {/* ✅ TEST BUTTON */}
            <button
                onClick={refetch}
                disabled={connected}
                className="mb-3 text-sm bg-gray-200 px-3 py-2 rounded disabled:opacity-50"
            >
                Verbindung prüfen
            </button>

            <div className="flex justify-between">
                <button
                    onClick={onBack}
                    disabled={autoAdvanced}
                >
                    Zurück
                </button>

                <button
                    onClick={onNext}
                    disabled={connected}
                    className="bg-indigo-600 text-white px-4 py-2 rounded disabled:opacity-50"
                >
                    Fertig
                </button>
            </div>

            {/* ✅ QR OVERLAY */}
            {showQR && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">
                    <div className="bg-white p-6 rounded-xl text-center">

                        <QRCodeSVG
                            value={JSON.stringify({
                                host: device.mqtt_host,
                                port: device.mqtt_port,
                                username: device.mqtt_username,
                                password: device.mqtt_password,
                                topic: topic
                            })}
                            size={260}
                        />

                        <div className="mt-4">
                            <button
                                onClick={() => setShowQR(false)}
                                className="bg-gray-200 px-4 py-2 rounded"
                            >
                                Schließen
                            </button>
                        </div>

                    </div>
                </div>
            )}

        </div>
    );
}

/* =========================================================
   STEP 4
========================================================= */

function StepWaiting({ device, onClose }) {

    const { data: devices } = useDeviceStatus();

    const status = devices?.find(d => d.identifier === device.identifier);

    if (status?.status === "online" || status?.status === "stale") {
        return (
            <div className="text-center">
                <h2>✅ Gerät verbunden</h2>
                <button onClick={onClose}>Dashboard</button>
            </div>
        );
    }

    return (
        <div className="text-center">
            <h2>⏳ Warte auf Daten...</h2>
        </div>
    );
}
