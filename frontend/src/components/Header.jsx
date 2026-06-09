/*
# src/components/Header.jsx
*/

import { Link } from "react-router-dom";

export default function Header({ theme, user }) {

    const primary = theme?.primary || "#f97316";
    const secondary = theme?.secondary || "#7c3aed";

    return (
        <header className="bg-white shadow-sm border-b">
            <div className="max-w-6xl mx-auto px-6 py-4 flex justify-between items-center">

                {/* LOGO */}
                <div
                    className="text-2xl font-bold"
                    style={{
                        background: `linear-gradient(to right, ${primary}, ${secondary})`,
                        WebkitBackgroundClip: "text",
                        color: "transparent",
                    }}
                >
                    Sharegy
                </div>

                {/* ✅ RECHTE SEITE */}
                <div className="flex items-center gap-4">

                    {/* 🔓 NICHT eingeloggt */}
                    {!user?.is_authenticated && (
                        <>
                            <Link
                                to="/login"
                                className="text-gray-600 hover:text-black"
                            >
                                Login
                            </Link>

                            <Link
                                to="/join"
                                className="bg-indigo-600 text-white px-4 py-2 rounded"
                            >
                                Beitreten
                            </Link>
                        </>
                    )}

                    {/* 🔐 eingeloggter User */}
                    {user?.is_authenticated && (
                        <>
                            <Link
                                to="/"
                                className="text-gray-600 hover:text-black"
                            >
                                Dashboard
                            </Link>

                            <button
                                onClick={() => {
                                    localStorage.removeItem("access");
                                    localStorage.removeItem("refresh");
                                    window.location.reload();
                                }}
                                className="text-red-600"
                            >
                                Logout
                            </button>
                        </>
                    )}

                </div>

            </div>
        </header>
    );
}

