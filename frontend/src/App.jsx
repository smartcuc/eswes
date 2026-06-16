/*
# src/App.jsx
*/

import { BrowserRouter, Routes, Route } from "react-router-dom";

import { ThemeProvider } from "./theme/ThemeContext";
import { defaultTheme } from "./theme/themes";

import { UserProvider } from "./context/UserContext";
import { SettingsProvider } from "./context/SettingsContext";
import AppRoutes from "./AppRoutes";   // ✅ PUBLIC
import PrivateApp from "./PrivateApp"; // ✅ PRIVATE
import AdminApp from "./AdminApp";     // ✅ ADMIN


export default function App() {

  return (
    <ThemeProvider theme={defaultTheme}>
      <UserProvider>   {/* 🔥 HIER */}
        <SettingsProvider>
          <BrowserRouter>

            <Routes>

              {/* 🔓 PUBLIC */}
              <Route path="/*" element={<AppRoutes />} />

              {/* 🔒 PRIVATE */}
              <Route path="/app/*" element={<PrivateApp />} />

              {/* 🔐 ADMIN */}
              <Route path="/admin/*" element={<AdminApp />} />

            </Routes>

          </BrowserRouter>
        </SettingsProvider>
      </UserProvider>
    </ThemeProvider>
  );
}
