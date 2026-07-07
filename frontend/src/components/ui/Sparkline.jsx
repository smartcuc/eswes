/*
# src/components/ui/Sparkline.jsx
*/

export default function Sparkline({
    values = [4, 8, 12, 10, 20, 15, 18, 9, 6],
}) {

    const max = Math.max(...values, 1);

    return (
        <div className="mt-3 h-12 flex items-end gap-1">

            {values.map((value, index) => (

                <div
                    key={index}
                    className="
                        flex-1
                        bg-indigo-500/70
                        rounded-sm
                    "
                    style={{
                        height: `${Math.max(
                            4,
                            (value / max) * 48
                        )}px`,
                    }}
                />

            ))}

        </div>
    );
}
