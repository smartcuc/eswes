/*
# components/overview/OverviewLayout.jsx
*/

import { useTheme } from "../../theme/ThemeContext";

export default function OverviewLayout({ children }) {
    const theme = useTheme();

    return (
        <div className={`min-h-screen ${theme.colors.bg}`}>
            <div className="max-w-6xl mx-auto p-6">
                {children}
            </div>
        </div>
    );
}


