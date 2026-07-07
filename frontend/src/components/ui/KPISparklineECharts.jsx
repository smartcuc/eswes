/*
# src/components/ui/KPISparklineECharts.jsx
*/

import ReactECharts from "echarts-for-react";

export default function KPISparklineECharts({
    values = [],
    color = "#2563eb",
}) {

    const option = {
        animation: false,

        grid: {
            top: 2,
            bottom: 2,
            left: 2,
            right: 2,
        },

        xAxis: {
            type: "category",
            show: false,
            data: values.map((_, i) => i),
        },

        yAxis: {
            type: "value",
            show: false,
            scale: true,
        },

        series: [
            {
                data: values,
                type: "line",
                smooth: true,

                showSymbol: false,

                lineStyle: {
                    width: 2,
                    color,
                },

                areaStyle: {
                    opacity: 0.08,
                    color,
                },
            },
        ],

        tooltip: {
            show: false,
        },
    };

    return (
        <div className="h-12 mt-2">
            <ReactECharts
                option={option}
                style={{
                    height: "100%",
                    width: "100%",
                }}
            />
        </div>
    );
}
