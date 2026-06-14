/*
# src/components/UserMenu.jsx
*/

import { useState, useRef, useEffect } from "react";
import { useUser } from "../hooks/useUser";
import { useTheme } from "../theme/ThemeContext";
import { Link } from "react-router-dom";

export default function UserMenu() {

    const theme = useTheme();
    const { user, refreshUser } = useUser();

    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);

    // ✅ Outside click schließen
    useEffect(() => {
        function handleClick(e) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setOpen(false);
            }
        }

        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    // ✅ Logout (Session-based)
    const logout = async () => {
        await fetch("/api/auth/logout/", {
            method: "POST",
            credentials: "include",
        });

        // ✅ sofort in Public wechseln
        window.location.replace("/");
        //refreshUser(); // ✅ UI sofort updaten
    };

    if (!user) return null;

    const displayName =
        user?.first_name
            ? `${user.first_name} ${user.last_name || ""}`
            : user?.email;

    const initials = user?.first_name
        ? `${user.first_name[0]}${user.last_name?.[0] || ""}`.toUpperCase()
        : user?.email?.[0]?.toUpperCase();

    return (
        <div className="relative" ref={dropdownRef}>

            {/* ✅ Button */}
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-3 px-2 py-1 rounded hover:bg-gray-100 transition"
            >
                <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium text-white"
                    style={{
                        background: `linear-gradient(
                            to right,
                            ${theme.primary || "#6366f1"},
                            ${theme.secondary || "#9333ea"}
                        )`,
                    }}
                >
                    {initials}
                </div>

                <span className="text-sm text-gray-700">
                    {displayName}
                </span>

                <span
                    className={`text-xs text-gray-400 transition-transform ${open ? "rotate-180" : ""
                        }`}
                >
                    ▾
                </span>
            </button>

            {/* ✅ Dropdown */}
            {open && (
                <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg py-2 z-50">

                    <div className="px-4 py-2 text-xs text-gray-500">
                        {user.email}
                    </div>

                    <div className="h-px bg-gray-100 my-1" />

                    <Link
                        to="/settings"
                        onClick={() => setOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-600 hover:bg-gray-50"
                    >
                        ⚙️ Einstellungen
                    </Link>

                    <button
                        onClick={logout}
                        className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50"
                    >
                        🚪 Logout
                    </button>

                </div>
            )}
        </div>
    );
}

