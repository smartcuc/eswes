/*
# src/components/layout/Sidebar.jsx
*/

import { NavLink } from "react-router-dom";
import { useUnconfiguredDevices } from "../../hooks/useUnconfiguredDevices";
import { useState } from "react";
import DeviceSetupModal from "../device/DeviceSetupModal";

const sections = [
    {
        title: null,
        items: [
            { name: "Dashboard", path: "/app/dashboard", icon: "🏠" },
        ],
    },
    {
        title: "Energy",
        items: [
            { name: "Overview", path: "/app/energy", icon: "⚡" },
        ],
    },
    {
        title: "Devices",
        items: [
            { name: "All Devices", path: "/app/devices", icon: "📟" },
            { name: "Add Device", action: "add_device", icon: "➕" },
        ],
    },
    {
        title: "Structure",
        items: [
            { name: "Floors", path: "/app/structure", icon: "🏡" },
        ],
    },
    {
        title: "Data",
        items: [
            { name: "Metrics", path: "/app/metrics", icon: "📊" },
        ],
    },

];

export default function Sidebar() {


    const query = useUnconfiguredDevices();

    const isLoaded = query?.isSuccess;
    const count = query?.data?.count ?? 0;
    const [openSetup, setOpenSetup] = useState(false);

    return (
        <div className="w-64 bg-white border-r flex flex-col">

            {/* ✅ Logo */}
            <div className="h-14 flex items-center px-4 border-b">
                <span className="font-bold text-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-transparent bg-clip-text">
                    ⚡ Sharegy
                </span>
            </div>

            {/* ✅ Navigation */}
            <div className="flex-1 overflow-auto p-3 space-y-4">


                {sections.map((section, idx) => (
                    <div key={idx}>

                        {/* Section Title */}
                        {section.title && (
                            <div className="text-xs text-gray-400 uppercase px-2 mb-1">
                                {section.title}
                            </div>
                        )}

                        {/* Items */}
                        <div className="space-y-1">
                            {section.items.map((item) => (

                                item.action === "add_device" ? (

                                    <button
                                        key="add"
                                        className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:bg-gray-100 rounded w-full text-left"
                                    >
                                        <span>{item.icon}</span>
                                        {item.name}
                                    </button>

                                ) : (

                                    <NavLink
                                        key={item.path}
                                        to={item.path}
                                        className={({ isActive }) =>
                                            `flex items-center gap-2 px-3 py-2 rounded text-sm transition ${isActive
                                                ? "bg-indigo-100 text-indigo-700"
                                                : "text-gray-600 hover:bg-gray-100"
                                            }`
                                        }
                                    >
                                        <span>{item.icon}</span>
                                        <span>{item.name}</span>

                                        {/* ✅ Badge */}
                                        {item.path === "/app/devices" && isLoaded && count > 0 && (

                                            <button
                                                onClick={(e) => {
                                                    e.preventDefault();
                                                    e.stopPropagation();
                                                    setOpenSetup(true);
                                                }}
                                                className="ml-auto text-xs bg-yellow-100 text-yellow-700 px-2 py-0.5 rounded-full hover:bg-yellow-200"
                                            >
                                                {count}
                                            </button>

                                        )}

                                    </NavLink>

                                )
                            ))}
                        </div>

                    </div>
                ))}

            </div>

            {/* ✅ MODAL */}
            <DeviceSetupModal
                open={openSetup}
                onClose={() => setOpenSetup(false)}
            />

        </div>
    );
}
