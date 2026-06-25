/*
# src/components/UserMenu.jsx
*/

import { useState, useRef, useEffect } from "react";
import { useUser } from "../hooks/useUser";
import { useTheme } from "../theme/ThemeContext";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";

export default function UserMenu() {

    const theme = useTheme();
    const { user } = useUser();
    const { logout } = useAuth();
    const navigate = useNavigate();

    const [open, setOpen] = useState(false);
    const dropdownRef = useRef(null);

    // ✅ Outside click schließen
    useEffect(() => {
        function handleClick(e) {
            if (
                dropdownRef.current &&
                !dropdownRef.current.contains(e.target)
            ) {
                setOpen(false);
            }
        }

        document.addEventListener("mousedown", handleClick);
        return () => document.removeEventListener("mousedown", handleClick);
    }, []);

    if (!user) return null;

    // ✅ Name & Initials
    const displayName =
        user?.first_name
            ? `${user.first_name} ${user.last_name || ""}`.trim()
            : user?.email;

    const initials =
        user?.first_name
            ? `${user.first_name[0]}${user.last_name?.[0] || ""}`.toUpperCase()
            : user?.email?.slice(0, 2).toUpperCase();

    async function handleLogout() {
        setOpen(false);
        await logout();

        // ✅ sauber zurück zur Landing
        navigate("/", { replace: true });
    }

    return (
        <div className="relative" ref={dropdownRef}>

            {/* BUTTON */}
            <button
                onClick={() => setOpen(!open)}
                className="flex items-center gap-3 px-2 py-1 rounded hover:bg-gray-100 transition"
            >
                <div
                    className="w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium text-white"
                    style={{
                        background: `linear-gradient(
                            to right,
                            ${theme.colors?.primary},
                            ${theme.colors?.secondary}
                        )`,
                    }}
                >
                    {initials}
                </div>

                <span className="text-sm text-gray-700">
                    {displayName}
                </span>

                <span className={`text-xs text-gray-400 transition-transform ${open ? "rotate-180" : ""}`}>
                    ▾
                </span>
            </button>

            {/* DROPDOWN */}
            {open && (
                <div className="absolute right-0 mt-2 min-w-[200px] bg-white border rounded-lg shadow-lg py-2 z-50">

                    <div className="px-4 py-2 text-xs text-gray-500">
                        {user.email}
                    </div>

                    <div className="h-px bg-gray-100 my-2 mx-2" />

                    {/* ✅ Settings */}
                    <Link
                        to="/app/settings"
                        onClick={() => setOpen(false)}
                        className="block px-4 py-2 text-sm text-gray-600 hover:bg-gray-50"
                    >
                        ⚙️ Einstellungen
                    </Link>

                    {/* ✅ Logout */}
                    <button
                        onClick={handleLogout}
                        className="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50"
                    >
                        🚪 Logout
                    </button>

                </div>
            )}

        </div>
    );
}
