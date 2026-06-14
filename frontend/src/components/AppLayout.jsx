/*
# src/components/AppLayout.jsx 
*/

import AppHeader from "./AppHeader";

export default function AppLayout({ children }) {
    return (
        <div className="min-h-screen bg-gray-50">

            <AppHeader />

            <main>
                {children}
            </main>

        </div>
    );
}
