/*
# src/components/tracking/FunnelChart.jsx
*/

import {
    FunnelChart,
    Funnel,
    Tooltip,
    LabelList,
} from "recharts";

export default function TrackingFunnel({ data }) {
    if (!data) return null;

    const formatted = data.steps.map((s) => ({
        name: s.label,
        value: s.count,
    }));

    return (
        <div className="bg-white p-4 rounded-xl shadow">
            <h3 className="mb-4 font-semibold">Funnel</h3>

            <FunnelChart width={400} height={250}>
                <Tooltip />
                <Funnel dataKey="value" data={formatted} isAnimationActive>
                    <LabelList position="right" fill="#000" stroke="none" />
                </Funnel>
            </FunnelChart>
        </div>
    );
}
