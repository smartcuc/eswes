/*
# TenantPageWrapper.jsx
*/


import { useParams } from "react-router-dom";
import DynamicPage from "./DynamicPage";

export default function TenantPageWrapper() {
    const { tenantSlug, pageSlug } = useParams();

    return (
        <DynamicPage
            tenantSlug={tenantSlug}
            pageSlug={pageSlug || "home"}   // ✅ wichtig!
        />
    );
}
