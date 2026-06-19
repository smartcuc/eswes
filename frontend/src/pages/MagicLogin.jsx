/*
# src/pages/MagicLogin.jsx
*/

import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { trackEvent } from "../lib/track";
import { useQueryClient } from "@tanstack/react-query";

export default function MagicLogin() {
    const navigate = useNavigate();
    const { token } = useParams();
    const queryClient = useQueryClient();

    const [status, setStatus] = useState("loading");

    useEffect(() => {
        if (!token) {
            navigate("/login", { replace: true });
            return;
        }

        async function run() {
            try {
                trackEvent("magic_login_attempt");

                // ✅ STEP 1 — Login
                const loginRes = await fetch(`/api/magic-login/?token=${token}`, {
                    credentials: "include",
                });

                if (!loginRes.ok) {
                    throw new Error("Login failed");
                }

                // ✅ STEP 2 — Session sicherstellen
                let meRes;

                for (let i = 0; i < 6; i++) {
                    meRes = await fetch("/api/auth/me/", {
                        credentials: "include",
                    });

                    if (meRes.ok) break;

                    await new Promise(r => setTimeout(r, 250));
                }

                if (!meRes || !meRes.ok) {
                    throw new Error("Session not ready");
                }

                // ✅ 🔥 PREFETCH (DAS MACHT DEN UNTERSCHIED)
                await queryClient.prefetchQuery({
                    queryKey: ["user"],
                    queryFn: async () => {
                        const res = await fetch("/api/auth/me/", {
                            credentials: "include",
                        });
                        return res.json();
                    }
                });

                await queryClient.prefetchQuery({
                    queryKey: ["settings"],
                    queryFn: async () => {
                        const res = await fetch("/api/settings/", {
                            credentials: "include",
                        });
                        return res.json();
                    }
                });

                trackEvent("magic_login_success");

                // ✅ STEP 3 — direkt rein
                navigate("/app/dashboard", { replace: true });

            } catch (err) {
                console.error("MagicLogin error:", err);

                setStatus("error");
                trackEvent("magic_login_failed");

                setTimeout(() => {
                    navigate("/login", { replace: true });
                }, 1500);
            }
        }

        run();
    }, [token, navigate, queryClient]);

    return (
        <div className="flex items-center justify-center h-screen">

            {status === "loading" && (
                <div className="text-center">
                    <div className="text-lg font-medium mb-2">
                        Logging you in...
                    </div>
                    <div className="text-gray-400 text-sm">
                        Please wait a moment
                    </div>
                </div>
            )}

            {status === "error" && (
                <div className="text-center text-red-500">
                    Login failed – redirecting...
                </div>
            )}

        </div>
    );
}
