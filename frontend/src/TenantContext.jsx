/*
# TenantContext.jsx
*/

import { createContext, useContext } from "react";

const TenantContext = createContext();

export function TenantProvider({ tenantSlug, children }) {
    return (
        <TenantContext.Provider value={{ tenantSlug }}>
            {children}
        </TenantContext.Provider>
    );
}

export function useTenant() {
    return useContext(TenantContext);
}
