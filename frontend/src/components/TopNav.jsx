/*
# src/components/TopNav.jsx
*/

import { Link } from "react-router-dom";

export default function TopNav({ user }) {
    return (
        <div className="flex justify-between items-center px-6 py-4 border-b bg-white">

            {/* Logo */}
            <div className="font-bold text-lg">
                Energy Platform
            </div>

            {/* Navigation rechts */}
            <div className="flex gap-4">

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
                            Community beitreten
                        </Link>
                    </>
                )}

                {user?.is_authenticated && (
                    <>
                        <Link
                            to="/"
                            className="text-gray-600"
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
    );
}
