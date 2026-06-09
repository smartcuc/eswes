/*
# src/pages/EnergyPage.jsx
*/

import { useParams } from "react-router-dom";
import EnergyFlow from "../components/EnergyFlow";

export default function EnergyPage() {
    const { tenantSlug } = useParams();

    return (
        <div style={{ padding: "2rem" }}>
            <h2>Energy Sharing verstehen</h2>
            <p>So wird Energie in deiner Community verteilt:</p>

            <EnergyFlow
                data={{
                    endpoint: `/api/v1/energy-flow/${tenantSlug}/`
                }}
            />
        </div>
    );
}