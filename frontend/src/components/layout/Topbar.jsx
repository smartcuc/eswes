/*
# src/components/layout/Topbar.jsx
*/

import { useUser } from "../../hooks/useUser";
import UserMenu from "../UserMenu";

export default function AppTopbar() {

    const { user } = useUser();

    // Später aus API beziehen
    const online = 12;
    const total = 14;

    return (
        <div className="h-14 bg-white border-b flex items-center justify-between px-4">

            {/* LEFT */}
            <div className="flex items-center gap-4">

                {/* 🏠 Home Switcher */}
                {user?.homes?.length > 1 && (
                    <select
                        className="
                            border
                            rounded-lg
                            px-3
                            py-1
                            text-sm
                            bg-white
                            hover:border-indigo-400
                        "
                    >
                        {user.homes.map((h) => (
                            <option
                                key={h.id}
                                value={h.id}
                            >
                                {h.name}
                            </option>
                        ))}
                    </select>
                )}

                {/* 📍 Kontext */}
                <div className="text-sm text-gray-400">
                    Dashboard
                </div>

            </div>

            {/* RIGHT */}
            <div className="flex items-center gap-4">

                {/* 📶 Geräte Status */}
                <div
                    className="
                        flex
                        items-center
                        gap-2
                        text-sm
                        text-gray-600
                    "
                >
                    <span className="w-2 h-2 bg-green-500 rounded-full"></span>

                    <span>
                        {online}/{total} Geräte online
                    </span>
                </div>

                {/* 👤 User */}
                <UserMenu user={user} />

            </div>

        </div>
    );
}