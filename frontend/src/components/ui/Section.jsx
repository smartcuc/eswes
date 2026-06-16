/*
# src/components/ui/Section.jsx
*/

export default function Section({ title, children }) {
    return (
        <div className="space-y-3">
            <h2 className="text-lg font-semibold">{title}</h2>
            <div className="bg-white rounded-2xl shadow p-4">
                {children}
            </div>
        </div>
    );
}
