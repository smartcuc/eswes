/*
# src/components/ui/Card.jsx
*/

import { useTheme, defaultTheme } from "../../theme/ThemeContext";

export default function Card({ children }) {
    const theme = useTheme() || defaultTheme;

    return (
        <div
            className={`
                ${theme.colors?.card || defaultTheme.colors.card}
                ${theme.radius?.lg || defaultTheme.radius.lg}
                ${theme.spacing?.card || defaultTheme.spacing.card}
                transition
            `}
        >
            {children}
        </div>
    );
}

