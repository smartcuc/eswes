/*
# src/components/tracking/KPI.jsx
*/

export default function KPI({ label, value }) {
    return (
        <div className="bg-white p-4 rounded-xl shadow">
            <div className="text-gray-400 text-sm">{label}</div>
            <div className="text-2xl font-semibold mt-1">{value}</div>
        </div>
    );
}
