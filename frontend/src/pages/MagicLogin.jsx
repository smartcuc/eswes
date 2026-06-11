/*
# src/pages/MagicLogin.jsx
*/

import { useEffect } from "react";

export default function MagicLogin() {

    useEffect(() => {
        const params = new URLSearchParams(window.location.search);
        const token = params.get("token");

        async function login() {
            if (!token) return;

            const res = await fetch(`/api/magic-login/?token=${token}`);
            const data = await res.json();

            if (res.ok && data.access) {
                localStorage.setItem("access", data.access);
                localStorage.setItem("refresh", data.refresh);

                window.location.href = "/";

                // ✅ Force full reload AFTER storage
                window.location.replace("/");

            } else {
                alert(data.error || "Login fehlgeschlagen");
            }
        }

        login();
    }, []);

    return (
        <div className="p-6 text-center">
            <h2 className="text-xl">Logging you in...</h2>
        </div>
    );
}