/*
# src/pages/MagicLogin.jsx
*/
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { trackEvent } from "../lib/track";

export default function MagicLogin() {
    const navigate = useNavigate();
    const { token } = useParams();

    const [status, setStatus] = useState("loading");

    useEffect(() => {
        if (!token) {
            navigate("/login", { replace: true });
            return;
        }

        async function run() {
            try {
                // ✅ TRACK: login attempt
                trackEvent("magic_login_attempt");

                // ✅ STEP 1 — Login
                const loginRes = await fetch(`/api/magic-login/?token=${token}`, {
                    credentials: "include",
                });

                if (!loginRes.ok) {
                    throw new Error("Login failed");
                }

                // ✅ STEP 2 — Session wait (race-safe)
                let meRes = await fetch("/api/auth/me/", {
                    credentials: "include",
                });

                if (!meRes.ok) {
                    await new Promise((r) => setTimeout(r, 150));

                    meRes = await fetch("/api/auth/me/", {
                        credentials: "include",
                    });

                    if (!meRes.ok) {
                        throw new Error("Session not ready");
                    }
                }

                // ✅ STEP 3 — Settings
                const settingsRes = await fetch("/api/settings/", {
                    credentials: "include",
                });

                if (!settingsRes.ok) {
                    throw new Error("Settings fetch failed");
                }

                const settings = await settingsRes.json();

                // ✅ TRACK: success
                trackEvent("magic_login_success");

                // ✅ STEP 4 — Routing
                if (settings.onboarding_step !== "done") {
                    navigate("/app", { replace: true });
                } else {
                    navigate("/app/dashboard", { replace: true });
                }

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
    }, [token, navigate]);

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