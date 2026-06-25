/*
# src/components/layout/Topbar.jsx
*/

import { useState } from "react";
import { useUser } from "../../hooks/useUser";
import AddDeviceModal from "../device/AddDeviceModal";
import UserMenu from "../UserMenu";

/* OPTIONAL HOOKS (falls vorhanden / später) */
// import { useDevices } from "../hooks/useDevices";

export default function AppTopbar() {

    const { user } = useUser();

    const [open, setOpen] = useState(false);
    const [home, setHome] = useState("Home 1");

    /* ✅ optional später */
    // const { data: devices } = useDevices();

    // const online = devices?.filter(d => d.status === "online").length || 0;
    // const total = devices?.length || 0;

    return (
        <div className="h-14 bg-white border-b flex items-center justify-between px-4">

            {/* ✅ LEFT: HOME + BREADCRUMB */}
            <div className="flex items-center gap-4">

                {/* 🔽 Home Switcher */}

                {user?.homes?.length > 1 && (
                    <select
                        className="border rounded px-2 py-1 text-sm"
                    >
                        {user.homes.map((h) => (
                            <option key={h.id} value={h.id}>
                                {h.name}
                            </option>
                        ))}
                    </select>
                )}

                {/* 📍 Context (Breadcrumb placeholder) */}
                <div className="text-sm text-gray-400">
                    Dashboard
                </div>

            </div>


            {/* ✅ CENTER: SEARCH */}
            <div className="hidden md:flex items-center w-1/3">

                <input
                    type="text"
                    placeholder="Search devices..."
                    className="w-full border rounded px-3 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-indigo-500"
                />

            </div>


            {/* ✅ RIGHT: STATUS + ACTIONS */}
            <div className="flex items-center gap-4">

                {/* 📶 SYSTEM STATUS */}
                <div className="flex items-center gap-2 text-sm">

                    {/* MQTT / WS Indicator */}
                    <div className="flex items-center gap-1">
                        <span className="w-2 h-2 bg-green-500 rounded-full"></span>
                        <span className="text-gray-500">Live</span>
                    </div>

                    {/* Device Count (optional später) */}
                    <div className="text-gray-400">
                        {/* {online}/{total} */}
                        12/14
                    </div>

                </div>

                {/* 🔍 USER MENU */}
                <UserMenu user={user} />

            </div>


            {/* ✅ MODAL */}
            <AddDeviceModal
                open={open}
                onClose={() => setOpen(false)}
            />

        </div>
    );
}

