/*
# src/components/tracking/DaysFilter.jsx
*/

export default function DaysFilter({ value, onChange }) {
    const options = [1, 7, 30];

    return (
        <div className="flex gap-2">
            {options.map((d) => (
                <button
                    key={d}
                    onClick={() => onChange(d)}
                    className={`px-3 py-1 rounded ${value === d
                            ? "bg-indigo-600 text-white"
                            : "bg-gray-100"
                        }`}
                >
                    {d}d
                </button>
            ))}
        </div>
    );
}
