import { useFunnel } from "../../hooks/useFunnel"
import { BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts"

export function FunnelChart() {
    const { data, isLoading } = useFunnel()

    if (isLoading) return <div>Loading...</div>

    return (
        <BarChart width={500} height={300} data={data}>
            <XAxis dataKey="label" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#8884d8" />
        </BarChart>
    )
}

