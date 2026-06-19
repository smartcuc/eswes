import { useKpis } from "../../hooks/useKpis"

export function KPICards() {
    const { data, isLoading } = useKpis()

    if (isLoading) return <div>Loading...</div>

    return (
        <div style={{ display: "flex", gap: "20px" }}>
            <div>
                <h3>DAU</h3>
                <p>{data.dau}</p>
            </div>

            <div>
                <h3>Landing → Signup</h3>
                <p>{data.conversion_landing_signup}%</p>
            </div>

            <div>
                <h3>Signup → Login</h3>
                <p>{data.conversion_signup_login}%</p>
            </div>
        </div>
    )
}