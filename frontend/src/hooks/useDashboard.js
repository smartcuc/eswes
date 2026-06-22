

import { useTrackingKPIs, useTrackingFunnel } from "./useTracking";
import { useDeviceStatus } from "./useDevices";

export function useDashboardData(days) {
    const kpis = useTrackingKPIs(days);
    const funnel = useTrackingFunnel(days);
    const devices = useDeviceStatus();

    return {
        kpis,
        funnel,
        devices,
        loading:
            kpis.isLoading ||
            funnel.isLoading ||
            devices.isLoading,
    };
}
