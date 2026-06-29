/*
# src/context/HomeContext.jsx
*/

import { createContext, useContext, useState, useEffect } from "react";

const HomeContext = createContext();

export function HomeProvider({ children }) {

    const [selectedHome, setSelectedHome] = useState(null);

    useEffect(() => {
        const stored = localStorage.getItem("selectedHome");
        if (stored) {
            setSelectedHome(JSON.parse(stored));
        }
    }, []);

    useEffect(() => {
        if (selectedHome !== null) {
            localStorage.setItem("selectedHome", JSON.stringify(selectedHome));
        }
    }, [selectedHome]);

    return (
        <HomeContext.Provider value={{ selectedHome, setSelectedHome }}>
            {children}
        </HomeContext.Provider>
    );
}

export function useHome() {
    return useContext(HomeContext);
}
