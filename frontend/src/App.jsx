/*
# App.jsx
*/

import { BrowserRouter } from "react-router-dom";
import { useUser } from "./hooks/useUser";

import { ThemeProvider } from "./theme/ThemeContext";
import { defaultTheme, buildTenantTheme } from "./theme/themes";

import AppRoutes from "./AppRoutes";
import Onboarding from "./pages/Onboarding";
import Overview from "./pages/Overview";

import TenantDashboard from "./pages/TenantDashboard";

export default function App() {
  const { user, loading } = useUser();

  if (loading) {
    return <div>Loading...</div>;
  }

  if (!user) return null;

  // ✅ Tenant bestimmen (simple rule)
  const activeTenant = user.memberships?.[0];

  const tenantTheme = buildTenantTheme(activeTenant);

  const theme = tenantTheme || defaultTheme;

  return (
    <ThemeProvider theme={theme}>
      <BrowserRouter>
        <SmartRouter user={user} />
      </BrowserRouter>
    </ThemeProvider>
  );
}


function SmartRouter({ user }) {


  if (!user) {
    return <div>Loading...</div>;
  }

  if (!user.is_authenticated) {
    return <AppRoutes />;
  }

  if (user.onboarding_step !== "done") {
    return <Onboarding />;
  }
  /*
    // ✅ tenant admin
    if (user.memberships?.length > 0) {
      const isAdmin = user.memberships.some(m => m.role === "admin");
      if (isAdmin) return <TenantDashboard />;
  
    }
  
    // ✅ TENANT USER
    if (user.memberships?.length > 0) {
      return <Overview mode="tenant" />;
    }
  */
  // ✅ STANDALONE USER
  return <Overview mode="user" />;
}


