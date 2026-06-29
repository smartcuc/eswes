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

// /*
// # src/components/AppLayout.jsx
// */

// import AppHeader from "./AppHeader";

// export default function AppLayout({ children }) {

//     const isDemo = window.location.pathname.startsWith("/demo");

//     return (
//         <div className="min-h-screen bg-gray-50">

//             {/* ✅ DEMO BANNER */}
//             {isDemo && (
//                 <div className="bg-blue-50 border-b border-blue-200 text-blue-800 text-sm px-4 py-2">
//                     🔍 Demo-Modus – Änderungen sind deaktiviert
//                 </div>
//             )}

//             <AppHeader />

//             <main>
//                 {children}
//             </main>

//         </div>
//     );
// }