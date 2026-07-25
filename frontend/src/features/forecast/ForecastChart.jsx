/*
# src/features/forecast/ForecastChart.jsx
*/

import { useMemo } from "react";
import ReactECharts from "echarts-for-react";
import { formatHour, formatNumber, formatDateTime, } from "../../utils/format";
import { useTimezone } from "../../hooks/useTimezone";

export default function ForecastChart({ points = [] }) {

    const FORECAST_COLOR = "#f59e0b";
    const timezone = useTimezone();

    const option = useMemo(() => {

        const xAxisData = points.map(
            p => formatHour(
                p.t * 1000,
                timezone
            )
        );

        const seriesData = points.map(
            p => Number(p.v)
        );

        return {
            tooltip: {
                trigger: "axis",

                formatter: function (params) {

                    const p = params[0];

                    const point =
                        points[p.dataIndex];

                    if (!point) {
                        return "";
                    }

                    return `
                        <b>
                            ${formatDateTime(
                        point.t * 1000,
                        timezone
                    )}
                        </b>
                        <br/>
                        ☀️ Forecast:
                        <b>
                            ${formatNumber(
                        p.value,
                        3
                    )} kWh
                        </b>
                    `;
                },
            },
            grid: {
                top: 20,
                left: 80,
                right: 20,
                bottom: 50,
            },

            xAxis: {
                type: "category",
                data: xAxisData,
                boundaryGap: false,
            },

            yAxis: {
                type: "value",

                axisLabel: {
                    formatter: value =>
                        `${formatNumber(value, 1)} kWh`,
                },
            },

            series: [
                {
                    name: "Solar Forecast",
                    type: "line",
                    smooth: true,
                    showSymbol: false,
                    data: seriesData,

                    lineStyle: {
                        width: 3,
                        color: FORECAST_COLOR,
                    },

                    areaStyle: {
                        opacity: 0.5,
                    },
                },
            ],
        };
    }, [points]);

    return (
        <ReactECharts
            option={option}
            style={{
                height: "400px",
                width: "100%",
            }}
        />
    );
}