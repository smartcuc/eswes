/*
# App.jsx
*/

import { BrowserRouter, Routes, Route } from "react-router-dom";

import LandingPage from "./LandingPage";
import TenantPage from "./TenantPage";
import TenantPageWrapper from "./TenantPageWrapper";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* ✅ Landing */}
        <Route path="/" element={<LandingPage />} />

        {/* ✅ Dashboard */}
        <Route path="/dashboard" element={<TenantPage />} />

        {/* ✅ Tenant Pages mit pageSlug (WICHTIG!) */}
        <Route
          path="/tenant/:tenantSlug/:pageSlug"
          element={<TenantPageWrapper />}
        />

        {/* ✅ Fallback für /tenant/xyz */}
        <Route
          path="/tenant/:tenantSlug"
          element={<TenantPageWrapper />}
        />

      </Routes>
    </BrowserRouter>
  );
}
