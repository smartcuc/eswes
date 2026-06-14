/*
# src/pages/Overview.jsx
*/

import { useUser } from "../hooks/useUser";
import OverviewUser from "./OverviewUser";
import OverviewTenant from "./OverviewTenant";

export default function Overview() {
    const { user } = useUser();

    const hasTenant = user?.memberships?.length > 0;

    if (hasTenant) {
        return <OverviewTenant />;
    }

    return <OverviewUser />;
}
