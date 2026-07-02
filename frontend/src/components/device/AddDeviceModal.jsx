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


/* =========================================================
   MAIN MODAL
========================================================= */

export default function AddDeviceModal({ open, onClose }) {

    const [step, setStep] = useState(1);
    const [connection, setConnection] = useState(null);
    const [name, setName] = useState("");
    const [device, setDevice] = useState(null);

    const createDevice = useCreateDevice();

    useEffect(() => {
        if (open) {
            setStep(1);
            setConnection(null);
            setName("");
            setDevice(null);
        }
    }, [open]);

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
            <div
                className={`
                    bg-white
                    text-gray-800
                    p-6
                    rounded-xl
                    w-full
                    relative
                    shadow-xl
                    ${step === 3 ? "max-w-3xl" : "max-w-lg"}
                `}
            >

                <div className="text-sm text-gray-400 mb-4">
                    Schritt {step} von 3
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

                            const identifier = name
                                .toLowerCase()
                                .replace(/ä/g, "ae")
                                .replace(/ö/g, "oe")
                                .replace(/ü/g, "ue")
                                .replace(/ß/g, "ss")
                                .replace(/\s+/g, "_")
                                .replace(/[^\w]/g, "")
                                .replace(/_+/g, "_")
                                .replace(/^_|_$/g, "");

                            try {

                                const result = await createDevice.mutateAsync({
                                    identifier,
                                    name
                                });

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
                        onClose={onClose}
                    />
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

    const options = [
        {
            key: "ha",
            icon: "🏠",
            title: "Home Assistant",
            description: "MQTT Integration nutzen"
        },
        {
            key: "iobroker",
            icon: "🔧",
            title: "ioBroker",
            description: "MQTT Adapter verbinden"
        },
        {
            key: "mqtt",
            icon: "📡",
            title: "MQTT",
            description: "Beliebiger MQTT Publisher"
        }
    ];

    return (
        <div>

            <h2 className="text-lg font-semibold mb-2">
                🔌 Datenquelle auswählen
            </h2>

            <p className="text-sm text-gray-500 mb-6">
                Wähle die Plattform aus, über die das Gerät Daten an Sharegy senden soll.
            </p>

            <div className="space-y-3">

                {options.map(option => (

                    <button
                        key={option.key}
                        onClick={() => onSelect(option.key)}
                        className="
                            w-full
                            text-left
                            p-4
                            border
                            border-gray-200
                            rounded-xl
                            bg-white
                            hover:bg-indigo-50
                            hover:border-indigo-300
                            transition
                        "
                    >

                        <div className="flex items-center gap-3">

                            <div className="text-2xl">
                                {option.icon}
                            </div>

                            <div>

                                <div className="font-medium text-gray-900">
                                    {option.title}
                                </div>

                                <div className="text-sm text-gray-500">
                                    {option.description}
                                </div>

                            </div>

                        </div>

                    </button>

                ))}

            </div>

        </div>
    );
}


/* =========================================================
   STEP 2
========================================================= */

function StepName({
    name,
    setName,
    onNext,
    onBack,
    loading
}) {

    function submit(e) {
        e.preventDefault();

        if (name && !loading) {
            onNext();
        }
    }

    return (
        <form onSubmit={submit}>

            <h2 className="text-lg font-semibold mb-2">
                🏷️ Gerät benennen
            </h2>

            <p className="text-sm text-gray-500 mb-6">
                Vergib einen eindeutigen Namen für das neue Gerät.
            </p>

            <div className="mb-6">

                <label className="text-sm font-medium text-gray-700 block mb-2">
                    Gerätename
                </label>

                <input
                    autoFocus
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    placeholder="z. B. Wärmepumpe"
                    className="
                        w-full
                        px-3
                        py-2
                        border
                        rounded-lg
                        focus:outline-none
                        focus:ring-2
                        focus:ring-indigo-500
                        focus:border-indigo-500
                    "
                />

                <div className="text-xs text-gray-400 mt-2">
                    Dieser Name wird später in Dashboard, Analytics und
                    Geräteübersicht angezeigt.
                </div>

            </div>

            <div className="flex justify-between">

                <button
                    type="button"
                    onClick={onBack}
                    disabled={loading}
                    className="
                        px-4
                        py-2
                        border
                        rounded-lg
                        disabled:opacity-50
                    "
                >
                    ← Zurück
                </button>

                <button
                    type="submit"
                    disabled={!name.trim() || loading}
                    className="
                        px-4
                        py-2
                        bg-indigo-600
                        hover:bg-indigo-700
                        text-white
                        rounded-lg
                        disabled:opacity-50
                    "
                >
                    {loading
                        ? "Gerät wird erstellt..."
                        : "Weiter →"}
                </button>

            </div>

        </form>
    );
}


/* =========================================================
   STEP 3 (CONFIG + VERIFY)
========================================================= */

function StepConfig({ device, onClose }) {

    const [copiedKey, setCopiedKey] = useState(null);
    const [showQR, setShowQR] = useState(false);

    const { data: devices } = useDeviceStatus();

    const topic = `home/${device.mqtt_token}/device/${device.identifier}`;

    const status = devices?.find(d => d.identifier === device.identifier);

    const connected =
        status?.status === "online" ||
        status?.status === "stale";

    const waiting = !connected;

    const [magicLoading, setMagicLoading] = useState(false);
    const [magicStatus, setMagicStatus] = useState(null);

    // ✅ AUTO CLOSE (nur einmal)
    useEffect(() => {

        if (!connected) {
            return;
        }

        const t = setTimeout(() => {
            onClose();
        }, 1200);

        return () => clearTimeout(t);

    }, [connected, onClose]);

    return (
        <div>

            <h2 className="text-lg font-semibold mb-2">
                📡 Gerät verbinden
            </h2>

            <p className="text-sm text-gray-500 mb-4">
                Richte dein Gerät für die Datenübertragung an Sharegy ein.
                Sobald die ersten Messwerte empfangen werden, wird dieses
                Fenster automatisch geschlossen.
            </p>

            {/* STATUS */}

            {connected && (
                <div className="mb-4 p-4 rounded-xl border border-green-200 bg-green-50">

                    <div className="font-medium text-green-800">
                        ✅ Erste Messwerte empfangen
                    </div>

                    <div className="text-sm text-green-700 mt-1">
                        Das Gerät sendet erfolgreich Messwerte an Sharegy.
                        Dieses Fenster wird automatisch geschlossen.
                    </div>

                </div>
            )}

            {waiting && (
                <div className="mb-4 p-4 rounded-xl border border-indigo-200 bg-indigo-50">

                    <div className="text-indigo-800 font-medium flex items-center gap-2">
                        <span className="animate-pulse">⏳</span>
                        Warte auf erste Messwerte
                    </div>

                    <div className="text-sm text-indigo-700 mt-1">
                        Sobald Sharegy Messwerte von diesem Gerät empfängt,
                        wird das Fenster automatisch geschlossen.
                    </div>

                </div>
            )}

            {/* QR + MQTT */}

            <div className="grid md:grid-cols-[1fr_2fr] gap-4 mb-4">

                {/* QR */}

                <div className="bg-white border rounded-xl p-4 text-center">

                    <div className="font-medium mb-3">
                        QR-Code
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
                                topic
                            })}
                            size={150}
                        />
                    </div>

                    <div className="text-xs text-gray-400 mt-3">
                        Zum Vergrößern anklicken
                    </div>

                </div>

                {/* MQTT DATEN */}

                <div className="bg-gray-50 border rounded-xl p-4">

                    <div className="font-medium mb-3">
                        MQTT Zugangsdaten
                    </div>

                    <div className="space-y-3 text-sm mb-4">

                        <div className="grid grid-cols-2 gap-4">

                            <div>
                                <div className="text-gray-500">Host</div>
                                <div className="font-medium">
                                    {device.mqtt_host}
                                </div>
                            </div>

                            <div>
                                <div className="text-gray-500">Port</div>
                                <div className="font-medium">
                                    {device.mqtt_port}
                                </div>
                            </div>

                        </div>

                        <div>
                            <div className="text-gray-500">Benutzer</div>
                            <div className="font-medium break-all">
                                {device.mqtt_username}
                            </div>
                        </div>

                        <div>
                            <div className="text-gray-500">Passwort</div>
                            <div className="font-medium break-all">
                                {device.mqtt_password}
                            </div>
                        </div>

                        <div>
                            <div className="text-gray-500">Topic</div>
                            <div className="text-indigo-600 break-all text-xs">
                                {topic}
                            </div>
                        </div>

                    </div>

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
                        className="w-full bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg"
                    >
                        {copiedKey === "all"
                            ? "✅ Zugangsdaten kopiert"
                            : "📋 Alle Zugangsdaten kopieren"}
                    </button>

                </div>

            </div>

            {/* MAIL */}

            <div className="border rounded-xl p-4 mb-4">

                <div className="font-medium mb-2">
                    📧 Konfiguration versenden
                </div>

                <div className="text-sm text-gray-500 mb-3">
                    Die MQTT-Zugangsdaten werden an deine hinterlegte
                    E-Mail-Adresse gesendet.
                </div>

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

                            if (navigator.clipboard) {
                                await navigator.clipboard.writeText(text);
                            }

                            await fetch("/api/devices/send-config/", {
                                method: "POST",
                                headers: {
                                    "Content-Type": "application/json",
                                    Authorization: `Bearer ${localStorage.getItem("token")}`
                                },
                                body: JSON.stringify({
                                    device
                                }),
                            });

                            setMagicStatus("success");

                        } catch {

                            setMagicStatus("error");

                        } finally {

                            setMagicLoading(false);
                        }

                    }}
                    disabled={magicLoading}
                    className="w-full bg-indigo-600 text-white px-4 py-2 rounded-lg disabled:opacity-50"
                >
                    {magicLoading
                        ? "Sende..."
                        : "✨ Setup senden + kopieren"}
                </button>

                {magicStatus === "success" && (
                    <div className="mt-3 text-sm text-green-600">
                        ✅ Mail gesendet und Daten kopiert
                    </div>
                )}

                {magicStatus === "error" && (
                    <div className="mt-3 text-sm text-red-600">
                        ❌ Fehler beim Senden
                    </div>
                )}

            </div>

            {/* FOOTER */}

            <div className="flex justify-end">

                <button
                    onClick={onClose}
                    className="px-4 py-2 border rounded-lg"
                >
                    Schließen
                </button>

            </div>

            {/* QR OVERLAY */}

            {showQR && (
                <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50">

                    <div className="bg-white p-6 rounded-2xl text-center">

                        <QRCodeSVG
                            value={JSON.stringify({
                                host: device.mqtt_host,
                                port: device.mqtt_port,
                                username: device.mqtt_username,
                                password: device.mqtt_password,
                                topic
                            })}
                            size={260}
                        />

                        <button
                            onClick={() => setShowQR(false)}
                            className="mt-4 bg-gray-200 px-4 py-2 rounded-lg"
                        >
                            Schließen
                        </button>

                    </div>

                </div>
            )}

        </div>
    );
}
