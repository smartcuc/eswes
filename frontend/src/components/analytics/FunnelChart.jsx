import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { useFunnel } from "../../hooks/useFunnel";

export function FunnelChart() {
    const { data, isLoading } = useFunnel();

    const option = useMemo(() => ({
        tooltip: {
            trigger: "axis",
        },

        grid: {
            top: 20,
            left: 40,
            right: 20,
            bottom: 40,
        },

        xAxis: {
            type: "category",
            data: (data || []).map(item => item.label),
        },

        yAxis: {
            type: "value",
        },

        series: [
            {
                type: "bar",
                data: (data || []).map(item => item.count),
                itemStyle: {
                    color: "#8884d8",
                },
            },
        ],
    }), [data]);

    if (isLoading) {
        return <div>Loading...</div>;
    }

    return (
        <ReactECharts
            option={option}
            style={{
                width: "500px",
                height: "300px",
            }}
        />
    );
}


