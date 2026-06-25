/*
# src/layouts/AppLayout.jsx
*/

import Sidebar from "../components/layout/Sidebar";
import Topbar from "../components/layout/Topbar";

export default function AppLayout({ children }) {
    return (
        <div className="flex h-screen bg-gray-50">

            {/* Sidebar */}
            <Sidebar />

            {/* Content Area */}
            <div className="flex-1 flex flex-col">

                {/* Topbar */}
                <Topbar />

                {/* Page Content */}
                <div className="flex-1 overflow-auto p-6">
                    {children}
                </div>

            </div>
        </div>
    );
}