/*
#
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../api/client";

import {
    LineChart,
    Line,
    XAxis,
    YAxis,
    Tooltip,
    ResponsiveContainer,
} from "recharts";

function formatStats(stats) {
    const map = {};
    stats.forEach((s) => {
        map[s.event] = s.count;
    });
    return map;
}

export default function TrackingDashboard() {
    const { data, isLoading } = useQuery({
        queryKey: ["tracking"],
        queryFn: () => apiFetch("/api/tracking/stats/"),
    });

    if (isLoading) {
        return <div className="p-6">Loading…</div>;
    }

    const stats = data.stats || [];
    const daily = data.daily || [];

    const map = formatStats(stats);

    const funnel = [
        "landing_view",
        "signup_click",
        "magic_link_requested",
        "email_open",
        "magic_link_click",
        "magic_login_success",
        "dashboard_open",
    ];

    return (
        <div className="p-6 space-y-8">

            {/* ✅ HEADER */}
            <h1 className="text-2xl font-semibold">Analytics</h1>

            {/* ✅ FUNNEL */}
            <div className="bg-white p-6 rounded-2xl shadow">
                <h2 className="text-lg font-medium mb-4">Conversion Funnel</h2>

                {funnel.map((step, i) => {
                    const value = map[step] || 0;
                    const prev = i === 0 ? value : (map[funnel[i - 1]] || 1);
                    const percent = i === 0 ? 100 : Math.round((value / prev) * 100);

                    return (
                        <div key={step} className="mb-4">
                            <div className="flex justify-between text-sm mb-1">
                                <span>{step}</span>
                                <span>{value} ({percent}%)</span>
                            </div>

                            <div className="h-3 bg-gray-100 rounded">
                                <div
                                    className="h-3 bg-indigo-500 rounded"
                                    style={{ width: `${percent}%` }}
                                />
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* ✅ CHART */}
            <div className="bg-white p-6 rounded-2xl shadow">
                <h2 className="text-lg font-medium mb-4">Events (Last 7 Days)</h2>

                <div style={{ width: "100%", height: 300 }}>
                    <ResponsiveContainer>
                        <LineChart data={daily}>
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Line
                                type="monotone"
                                dataKey="count"
                                stroke="#6366f1"
                                strokeWidth={2}
                            />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* ✅ TOP EVENTS */}
            <div className="bg-white p-6 rounded-2xl shadow">
                <h2 className="text-lg font-medium mb-4">Top Events</h2>

                {stats
                    .sort((a, b) => b.count - a.count)
                    .slice(0, 10)
                    .map((item) => (
                        <div
                            key={item.event}
                            className="flex justify-between py-1 text-sm"
                        >
                            <span>{item.event}</span>
                            <span>{item.count}</span>
                        </div>
                    ))}
            </div>

        </div>
    );
}
