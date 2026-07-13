/*
# src/pages/admin/AdminDashboard.jsx
*/

import { useEffect, useState } from "react";
import AdminLayout from "../../components/admin/AdminLayout";
import { KpiCard } from "../../components/admin/KpiCard";
import ReactECharts from "echarts-for-react";


export default function AdminDashboard() {
    const [data, setData] = useState(null);

    useEffect(() => {
        fetch("/api/stats/dashboard/", {
            credentials: "include",
        })
            .then((res) => res.json())
            .then(setData)
            .catch(console.error);
    }, []);

    if (!data) return <div className="p-6">Loading...</div>;

    const funnel = [
        { name: "Total", value: data.funnel.total },
        { name: "Opened", value: data.funnel.opened },
        { name: "Clicked", value: data.funnel.clicked },
        { name: "Login", value: data.funnel.used },
    ];

    const chartOption = {
        tooltip: {
            trigger: "axis",
        },
        xAxis: {
            type: "category",
            data: funnel.map(f => f.name),
        },
        yAxis: {
            type: "value",
        },
        series: [
            {
                type: "bar",
                data: funnel.map(f => f.value),
                itemStyle: {
                    color: "#4f46e5",
                },
                barWidth: "50%",
            },
        ],
    };

    return (
        <AdminLayout>

            {/* KPI */}
            <div className="grid grid-cols-4 gap-4 mb-6">
                <KpiCard title="Total Links" value={data.funnel.total} />
                <KpiCard title="Opened" value={data.funnel.opened} />
                <KpiCard title="Clicks" value={data.funnel.clicked} />
                <KpiCard title="Logins" value={data.funnel.used} />
            </div>

            {/* CHART */}
            <div className="bg-white p-6 rounded-2xl shadow mb-6">
                <h2 className="mb-4 font-semibold">Conversion Funnel</h2>

                <ReactECharts
                    option={chartOption}
                    style={{
                        width: "100%",
                        height: "300px",
                    }}
                />
            </div>

            {/* LIVE LOGINS */}
            <div className="bg-white p-6 rounded-2xl shadow">
                <h2 className="mb-4 font-semibold">Live Activity</h2>

                <div className="space-y-2">
                    {data.live_logins?.map((l, i) => (
                        <div key={i} className="text-sm text-gray-600">
                            ✅ {l.user} logged in at {l.timestamp}
                        </div>
                    ))}
                </div>
            </div>

        </AdminLayout>
    );
}
