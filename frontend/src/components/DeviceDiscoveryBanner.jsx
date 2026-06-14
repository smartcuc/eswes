/*
# src/components/DeviceDiscoveryBanner.jsx
*/

export default function DeviceDiscoveryBanner({ devices, onOpen }) {
    if (!devices || !devices.unconfigured?.length) return null;

    return (
        <div className="bg-yellow-100 border border-yellow-300 p-4 rounded-xl mb-4">
            <div className="flex justify-between items-center">
                <div>
                    <strong>Neue Geräte erkannt</strong> ({devices.unconfigured.length})
                </div>

                <button
                    onClick={onOpen}
                    className="bg-black text-white px-4 py-2 rounded-lg"
                >
                    Jetzt konfigurieren
                </button>
            </div>
        </div>
    );
}
