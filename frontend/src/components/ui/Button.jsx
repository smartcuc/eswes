/*
# src/components/ui/Button.jsx
*/

import { useTheme } from "../../theme/ThemeContext";

export default function Button({ children, onClick, variant = "primary" }) {
    const theme = useTheme();

    const variants = {
        primary: "text-white",
        secondary: "border text-gray-700",
    };

    return (
        <button
            onClick={onClick}
            className={`
                px-4 py-2
                ${theme.radius.md}
                ${variants[variant]}
                transition-all duration-150
                active:scale-[0.97]
            `}
            style={{
                background:
                    variant === "primary" ? theme.primary : "transparent",
                borderColor:
                    variant === "secondary" ? "#e5e7eb" : "transparent",
            }}
        >
            {children}
        </button>
    );
}
