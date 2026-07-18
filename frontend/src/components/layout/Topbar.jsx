/*
# src/components/layout/Topbar.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { apiFetch } from "../../api/client";
import { useUser } from "../../hooks/useUser";
import UserMenu from "../UserMenu";
import SpotPriceModal from "../../features/market/components/SpotPriceModal";

export default function AppTopbar() {

    const { user } = useUser();
    // Später aus API beziehen
    const online = 12;
    const total = 14;

    const spotPriceQuery = useQuery({
        queryKey: ["spot-price"],
        queryFn: () =>
            apiFetch("/api/market/current/"),
        refetchInterval: 60000,
    });

    const spotPrice = spotPriceQuery.data;

    const spotColor =
        spotPrice?.status === "good"
            ? "text-green-600"
            : spotPrice?.status === "warning"
                ? "text-amber-600"
                : "text-red-600";

    const [spotModalOpen, setSpotModalOpen] =
        useState(false);

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

                {spotPrice && (
                    <button
                        onClick={() => setSpotModalOpen(true)}
                        title="Aktueller Börsenstrompreis (EPEX Spot)"
                        className={`
                            flex
                            items-center
                            gap-1
                            text-sm
                            font-semibold
                            ${spotColor}

                            hover:opacity-80
                            transition-opacity
                            cursor-pointer
                        `}
                    >
                        <span>💰</span>

                        <span>
                            {spotPrice.price_ct.toFixed(2)} ct/kWh
                        </span>
                    </button>
                )}

                <UserMenu user={user} />
                <SpotPriceModal
                    open={spotModalOpen}
                    onClose={() =>
                        setSpotModalOpen(false)
                    }
                />
            </div>

        </div>
    );
}