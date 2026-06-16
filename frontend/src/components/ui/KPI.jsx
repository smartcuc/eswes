/*
# src/components/ui/KPI.jsx
*/

import Card from "./Card";

export default function KPI({ label, value, unit = "", icon }) {
    return (
        <Card className="flex items-center gap-4">

            {icon && (
                <div className="text-xl">
                    {icon}
                </div>
            )}

            <div>
                <p className="text-sm text-gray-500">
                    {label}
                </p>

                <p className="text-xl font-semibold">
                    {value ?? 0} {unit}
                </p>
            </div>

        </Card>
    );
}
