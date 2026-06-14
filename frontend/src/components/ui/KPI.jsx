/*
# src/components/ui/KPI.jsx
*/

export default function KPI({ label, value }) {
    return (
        <div className="bg-white border border-gray-100 rounded-2xl p-5 transition hover:shadow-md">

            <p className="text-sm text-gray-500 mb-1">
                {label}
            </p>

            <p className="text-2xl font-bold">
                {value ?? 0} kWh
            </p>

        </div>
    );
}
