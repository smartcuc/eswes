/*
# src/components/tracking/FunnelChart.jsx
*/

import { useMemo } from "react";
import ReactECharts from "echarts-for-react";

export default function TrackingFunnel({ data }) {

    if (!data) {
        return null;
    }

    const formatted = data.steps.map((s) => ({
        name: s.label,
        value: s.count,
    }));

    const option = useMemo(() => ({
        tooltip: {
            trigger: "item",
            formatter: "{b}: {c}",
        },

        series: [
            {
                type: "funnel",

                left: "10%",
                top: 10,
                bottom: 10,
                width: "80%",

                sort: "descending",

                label: {
                    show: true,
                    position: "right",
                    color: "#000",
                    formatter: "{b}: {c}",
                },

                itemStyle: {
                    borderColor: "#fff",
                    borderWidth: 2,
                },

                data: formatted,
            },
        ],
    }), [formatted]);

    return (
        <div className="bg-white p-4 rounded-xl shadow">
            <h3 className="mb-4 font-semibold">
                Funnel
            </h3>

            <ReactECharts
                option={option}
                style={{
                    width: "400px",
                    height: "250px",
                }}
            />
        </div>
    );
}