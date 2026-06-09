/*
# src/pages/TenantDashboard.jsx
*/

import { useEffect, useState } from "react";

import { apiFetch } from "../api";
import { texts } from "../i18n";
import { useLang } from "../hooks/useLang";


export default function TenantDashboard() {
    const [tenant, setTenant] = useState(null);
    const [members, setMembers] = useState([]);
    const [invites, setInvites] = useState([]);
    const [logs, setLogs] = useState([]);

    const { lang } = useLang();
    const t = texts[lang];

    // ✅ Zentrale Ladefunktion
    function loadData() {
        // Tenant + Members + Invites
        apiFetch("/api/my-tenant/")
            .then(res => res.json())
            .then(data => {
                setTenant(data.tenant);
                setMembers(data.members || []);
                setInvites(data.invites || []);
            });

        // Audit Logs
        fetch("/api/audit-log/")
            .then(res => res.json())
            .then(data => {
                setLogs(data || []);
            });
    }

    useEffect(() => {
        loadData();
    }, []);

    // ✅ INVITE ERSTELLEN
    async function createInvite(role) {
        const res = await apiFetch("/api/create-invite/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                tenant_id: tenant.id,
                role: role,
            }),
        });

        const data = await res.json();

        // Refresh UI
        loadData();

        alert(`${t.invite_link}:\n${window.location.origin}${data.link}`);
    }

    // ✅ ROLE UPDATE
    async function updateRole(userId, role) {
        await apiFetch("/api/update-role/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
                role: role,
            }),
        });

        loadData();
    }

    // ✅ MEMBER ENTFERNEN
    async function removeMember(userId) {
        await apiFetch("/api/remove-member/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                tenant_id: tenant.id,
                user_id: userId,
            }),
        });

        loadData();
    }

    // ✅ INVITE DEAKTIVIEREN
    async function deactivateInvite(token) {
        await apiFetch("/api/deactivate-invite/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
        });

        loadData();
    }

    // ✅ FORMAT ACTION TEXT
    function formatAction(log) {
        switch (log.action) {
            case "member_removed":
                return t.member_removed || "Mitglied entfernt";

            case "role_updated":
                return t.role_updated || "Rolle geändert";

            case "invite_created":
                return t.invite_created || "Invite erstellt";

            case "invite_deactivated":
                return t.invite_deactivated || "Invite deaktiviert";

            default:
                return log.action;
        }
    }

    // ✅ FORMAT DATE
    function formatDate(date) {
        return new Date(date).toLocaleString();
    }

    return (
        <div className="p-6 max-w-4xl mx-auto">

            {/* ✅ TITLE */}
            <h1 className="text-2xl font-bold mb-6">
                {t.tenant_dashboard} – {tenant?.name}
            </h1>

            {/* ✅ INVITES */}
            <section className="mb-8">
                <h2 className="text-lg font-semibold mb-3">
                    {t.invites}
                </h2>

                {/* ✅ CREATE */}
                <div className="flex gap-2 mb-4">
                    <button
                        onClick={() => createInvite("viewer")}
                        className="bg-indigo-600 text-white px-4 py-2 rounded"
                    >
                        {t.viewer_invite}
                    </button>

                    <button
                        onClick={() => createInvite("editor")}
                        className="bg-gray-700 text-white px-4 py-2 rounded"
                    >
                        {t.editor_invite}
                    </button>

                    <button
                        onClick={() => createInvite("admin")}
                        className="bg-red-600 text-white px-4 py-2 rounded"
                    >
                        {t.admin_invite}
                    </button>
                </div>

                {/* ✅ LIST */}
                <div className="space-y-2">
                    {invites.map(i => (
                        <div key={i.token} className="border p-3 rounded flex flex-col">

                            <div className="flex justify-between">
                                <span className="text-sm text-gray-500">
                                    {i.role}
                                </span>

                                <span className="text-xs text-gray-400">
                                    used: {i.used}
                                </span>
                            </div>

                            <div className="text-xs break-all mt-1">
                                {window.location.origin}/onboarding?invite={i.token}
                            </div>

                            <div className="flex gap-3 mt-2">

                                <button
                                    onClick={() =>
                                        navigator.clipboard.writeText(
                                            window.location.origin + "/onboarding?invite=" + i.token
                                        )
                                    }
                                    className="text-indigo-600 text-xs"
                                >
                                    Copy
                                </button>

                                <button
                                    onClick={() => deactivateInvite(i.token)}
                                    className="text-red-500 text-xs"
                                >
                                    Deaktivieren
                                </button>

                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* ✅ MEMBERS */}
            <section>
                <h2 className="text-lg font-semibold mb-3">
                    {t.members}
                </h2>

                <div className="space-y-2">
                    {members.map(m => (
                        <div
                            key={m.id}
                            className="border p-3 rounded flex justify-between items-center"
                        >
                            <span>{m.email}</span>

                            <div className="flex gap-2 items-center">

                                <select
                                    value={m.role}
                                    onChange={(e) =>
                                        updateRole(m.id, e.target.value)
                                    }
                                    className="text-sm border rounded p-1"
                                >
                                    <option value="viewer">Viewer</option>
                                    <option value="editor">Editor</option>
                                    <option value="admin">Admin</option>
                                </select>

                                <button
                                    onClick={() => removeMember(m.id)}
                                    className="text-red-600 text-sm"
                                >
                                    Entfernen
                                </button>

                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* ✅ AUDIT LOG */}
            <section className="mt-10">
                <h2 className="text-lg font-semibold mb-3">
                    {t.audit_log || "Aktivität"}
                </h2>

                <div className="space-y-2 max-h-80 overflow-y-auto">

                    {logs
                        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                        .slice(0, 30)
                        .map((log, idx) => (

                            <div
                                key={idx}
                                className={`border p-3 rounded text-sm ${log.action === "member_removed"
                                    ? "border-red-400"
                                    : ""
                                    }`}
                            >
                                <div className="flex justify-between">
                                    <span className="font-medium">
                                        {formatAction(log)}
                                    </span>

                                    <span className="text-gray-400 text-xs">
                                        {formatDate(log.created_at)}
                                    </span>
                                </div>

                                <div className="text-xs text-gray-500 mt-1">
                                    {log.user} → {log.target || "-"}
                                </div>

                            </div>
                        ))}

                </div>
            </section>

        </div>
    );
}

