/*
# src/theme/ThemeContext.jsx
*/

import { createContext, useContext } from "react";

const ThemeContext = createContext();

export function ThemeProvider({ theme, children }) {
    return (
        <ThemeContext.Provider value={theme}>
            {children}
        </ThemeContext.Provider>
    );
}

export function useTheme() {
    return useContext(ThemeContext);
}
