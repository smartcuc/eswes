/*
# components/admin/AdminLayout.jsx
*/

import { Link } from "react-router-dom";

export default function AdminLayout({ children }) {
    return (
        <div className="flex h-screen bg-gray-100">

            {/* Sidebar */}
            <aside className="w-64 bg-white shadow-lg p-5">
                <h2 className="text-xl font-bold mb-8">Sharegy Admin</h2>

                <nav className="space-y-2">
                    <Link to="/admin/dashboard" className="block px-3 py-2 rounded hover:bg-gray-100">
                        Dashboard
                    </Link>
                </nav>
            </aside>

            {/* Content */}
            <main className="flex-1 flex flex-col">

                {/* Header */}
                <div className="bg-white border-b p-4 flex justify-between">
                    <div className="font-semibold">Dashboard</div>
                    <div className="text-sm text-gray-500">Admin</div>
                </div>

                {/* Body */}
                <div className="p-6 overflow-auto">
                    {children}
                </div>
            </main>
        </div>
    );
}
