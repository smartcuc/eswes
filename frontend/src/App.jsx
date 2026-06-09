/*
# App.jsx
*/

import { BrowserRouter } from "react-router-dom";
import { useUser } from "./hooks/useUser";

import AppRoutes from "./AppRoutes";
import Onboarding from "./pages/Onboarding";
import Dashboard from "./pages/Dashboard";
import TenantDashboard from "./pages/TenantDashboard";

export default function App() {
  const user = useUser();

  // ⏳ noch loading
  if (!user) return null;

  return (
    <BrowserRouter>
      <SmartRouter user={user} />
    </BrowserRouter>
  );
}

function SmartRouter({ user }) {

  if (!user) {
    return <div>Loading...</div>;
  }

  // ✅ nicht eingeloggt
  if (!user.is_authenticated) {
    return <AppRoutes />;   // enthält Landing + /login
  }

  // ✅ onboarding
  if (user.onboarding_step !== "done") {
    return <Onboarding />;
  }

  // ✅ tenant admin
  if (user.memberships?.length > 0) {
    const isAdmin = user.memberships.some(m => m.role === "admin");
    if (isAdmin) return <TenantDashboard />;
  }

  // ✅ standalone
  if (user.usage_mode === "standalone") {
    return <Dashboard />;
  }

  return <AppRoutes />;
}