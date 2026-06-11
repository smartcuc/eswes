/*
# components/overview/OverviewLayout.jsx
*/

import { useTheme } from "../../theme/ThemeContext";

export default function OverviewLayout({ data, loading }) {
    const theme = useTheme();

    if (loading) {
        return (
            <div className={`min-h-screen p-6 ${theme.colors.bg}`}>
                <p>Lade Daten...</p>
            </div>
        );
    }

    return (
        <div className={`min-h-screen p-6 ${theme.colors.bg}`}>

            {/* Header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold">Übersicht</h1>
                <p className="text-gray-500">
                    Deine Energie auf einen Blick
                </p>
            </div>

            {/* KPI Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

                <KPI title="Verbrauch" value={data?.consumption_kwh} theme={theme} />
                <KPI title="Erzeugung" value={data?.generation_kwh} theme={theme} />
                <KPI title="Netzbezug" value={data?.grid_import_kwh} theme={theme} />
                <KPI title="Einspeisung" value={data?.grid_export_kwh} theme={theme} />

            </div>

            {/* CTA */}
            {data?.consumption_kwh === 0 && (
                <EmptyState theme={theme} />
            )}

            {/* Beispiel Button */}
            <button
                className={`mt-6 px-4 py-2 rounded ${theme.colors.accent} ${theme.colors.accentText}`}
            >
                Zähler hinzufügen
            </button>

        </div>
    );
}


function KPI({ title, value, theme }) {
    return (
        <div className={`shadow rounded-lg p-4 ${theme.colors.card}`}>
            <p className="text-gray-500 text-sm">{title}</p>
            <p className="text-xl font-semibold">
                {value ?? 0} kWh
            </p>
        </div>
    );
}


function EmptyState({ theme }) {
    return (
        <div className={`mt-6 p-4 rounded-lg ${theme.colors.card}`}>
            <p>Noch keine Daten vorhanden.</p>
        </div>
    );
}


