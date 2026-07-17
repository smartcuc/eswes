/*
# src/features/market/components/SpotPriceModal.jsx
*/

import { useQuery } from "@tanstack/react-query";
import { apiFetch } from "../../../api/client";

export default function SpotPriceModal({
    open,
    onClose,
}) {

    const { data } = useQuery({
        queryKey: ["spot-price-chart"],
        queryFn: () =>
            apiFetch(
                "/api/market/chart/"
            ),
        enabled: open,
    });

    if (!open) {
        return null;
    }

    return (
        <div
            className="
                fixed inset-0
                bg-black/40
                flex items-center justify-center
                z-50
            "
            onClick={onClose}
        >
            <div
                className="
                    bg-white
                    rounded-2xl
                    p-6
                    w-full
                    max-w-4xl
                "
                onClick={(e) =>
                    e.stopPropagation()
                }
            >

                <h3
                    className="
                        text-xl
                        font-semibold
                        mb-4
                    "
                >
                    ⚡ Spotpreis
                </h3>

                {data && (
                    <div
                        className="
            grid
            grid-cols-4
            gap-3
            mb-6
        "
                    >

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Aktuell
                            </div>

                            <div className="font-semibold text-indigo-600">
                                {data.current?.toFixed(2)} ct
                            </div>
                        </div>

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Minimum
                            </div>

                            <div className="font-semibold text-green-600">
                                {data.min?.toFixed(2)} ct
                            </div>
                        </div>

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Maximum
                            </div>

                            <div className="font-semibold text-red-600">
                                {data.max?.toFixed(2)} ct
                            </div>
                        </div>

                        <div className="bg-slate-50 rounded-lg p-3">
                            <div className="text-xs text-gray-500">
                                Durchschnitt
                            </div>

                            <div className="font-semibold text-gray-700">
                                {data.avg?.toFixed(2)} ct
                            </div>
                        </div>

                    </div>
                )}

            </div>
        </div>
    );
}
