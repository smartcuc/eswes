/*
# src/context/SettingsContext.jsx
*/

import { createContext, useContext, useEffect, useState, useRef } from "react";

const SettingsContext = createContext();

export function SettingsProvider({ children }) {
    const [settings, setSettings] = useState(null);

    const loadingRef = useRef(false);

    useEffect(() => {
        if (settings || loadingRef.current) return;

        loadingRef.current = true;

        fetch("/api/settings/", {
            credentials: "include",
        })
            .then(res => res.ok ? res.json() : null)
            .then(data => {
                if (data) setSettings(data);
            })
            .finally(() => {
                loadingRef.current = false;
            });

    }, [settings]);

    return (
        <SettingsContext.Provider value={{ settings, setSettings }}>
            {children}
        </SettingsContext.Provider>
    );
}

export function useSettings() {
    return useContext(SettingsContext);
}
