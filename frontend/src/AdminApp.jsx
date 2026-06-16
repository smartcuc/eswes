/*
# src/AdminApp.jsx
*/

import { Routes, Route, Navigate } from "react-router-dom";
import AdminDashboard from "./pages/admin/AdminDashboard";

export default function AdminApp() {

    const user = JSON.parse(localStorage.getItem("user"));
    const loading = false;

    if (loading) return <div>Loading...</div>;

    if (!user) return <Navigate to="/login" />;
    if (!user.is_staff) return <Navigate to="/app/dashboard" />;

    return (
        <div style={{ padding: 20 }}>
            <h1>Admin Panel</h1>

            <Routes>
                <Route index element={<AdminDashboard />} />
                <Route path="dashboard" element={<AdminDashboard />} />
            </Routes>

        </div>
    );
}
