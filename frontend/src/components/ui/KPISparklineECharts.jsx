/* Test mit 0-line
# src/components/ui/KPISparklineECharts.jsx
*/

import ReactECharts from "echarts-for-react";

export default function KPISparklineECharts({
    values = [],
    color = "#2563eb",
    chartType = "line",
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
                type: chartType,

                // series: [
                //     {
                //         data: values,
                //         type: "line",

                smooth: chartType === "line",

                showSymbol: false,

                lineStyle: {
                    width: 2,
                    color,
                },

                areaStyle:
                    chartType === "line"
                        ? {
                            opacity: 0.08,
                            color,
                        }
                        : undefined,

                itemStyle: {
                    color,
                    borderRadius: [2, 2, 0, 0],
                },

                markLine:
                    chartType === "line"
                        ? {
                            silent: true,
                            symbol: "none",

                            lineStyle: {
                                color: "#e5e7eb",
                                width: 1,
                                type: "dashed",
                            },

                            data: [
                                {
                                    yAxis: 0,
                                },
                            ],
                        }
                        : undefined,
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
