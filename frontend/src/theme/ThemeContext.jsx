/*
# src/theme/ThemeContext.jsx
*/

import React, { createContext, useContext } from "react";

const ThemeContext = createContext(null);


// ✅ DEFAULT THEME
export const defaultTheme = {
    colors: {
        bg: "bg-gray-50",
        card: "bg-white border border-gray-200",

        primary: "#6366f1",
        secondary: "#9333ea",

        text: "text-gray-900",
        textMuted: "text-gray-500",

        border: "border-gray-200",
        hover: "hover:bg-gray-100",
    },

    radius: {
        md: "rounded-lg",
        lg: "rounded-2xl",
    },

    spacing: {
        section: "mb-10",
        card: "p-6",
    },
};


// ✅ PROVIDER
export function ThemeProvider({ theme = {}, children }) {
    return (
        <ThemeContext.Provider value={theme}>
            {children}
        </ThemeContext.Provider>
    );
}


// ✅ HOOK
export function useTheme() {
    const context = useContext(ThemeContext);

    // ✅ SAFE MERGE (entscheidend!)
    return {
        ...defaultTheme,
        ...context,
        colors: {
            ...defaultTheme.colors,
            ...context?.colors,
        },
        radius: {
            ...defaultTheme.radius,
            ...context?.radius,
        },
        spacing: {
            ...defaultTheme.spacing,
            ...context?.spacing,
        },
    };
}

