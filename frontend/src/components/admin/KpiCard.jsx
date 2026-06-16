
/*# components/admin/KpiCard.jsx
*/

export function KpiCard({ title, value }) {
    return (
        <div className="bg-white p-5 rounded-2xl shadow">
            <div className="text-gray-500 text-sm">{title}</div>
            <div className="text-2xl font-bold mt-1">{value}</div>
        </div>
    );
}
