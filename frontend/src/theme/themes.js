/*
# src/theme/themes.js
*/

export const defaultTheme = {
    name: "default",
    colors: {
        bg: "bg-gray-50",
        card: "bg-white",
        accent: "bg-indigo-600",
        accentText: "text-white",
    },
};

export function buildTenantTheme(tenant) {
    if (!tenant?.theme) return null;

    // ✅ Mapping fix
    const colorMap = {
        green: {
            bg: "bg-green-50",
            accent: "bg-green-600",
        },
        blue: {
            bg: "bg-blue-50",
            accent: "bg-blue-600",
        },
        red: {
            bg: "bg-red-50",
            accent: "bg-red-600",
        },
    };

    const base = colorMap[tenant.theme.primary] || colorMap.green;

    return {
        name: tenant.name,
        colors: {
            bg: base.bg,
            card: "bg-white",
            accent: base.accent,
            accentText: "text-white",
        },
    };
}
