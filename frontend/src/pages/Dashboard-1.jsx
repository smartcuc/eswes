/*
# src/pages/Dashboard.jsx
*/

import { useState, useEffect } from "react";
import Footer from "../components/Footer";

import Impressum from "../pages/Impressum";
import Datenschutz from "../pages/Datenschutz";

export default function Dashboard() {

    const [showImpressum, setShowImpressum] = useState(false);
    const [showDatenschutz, setShowDatenschutz] = useState(false);

    return (
        <div className="p-6">
            <h1 className="text-2xl font-bold mb-4">
                User Dashboard
            </h1>

            <p>✅ Login erfolgreich</p>
            <p>✅ API funktioniert</p>
            <p>✅ System läuft</p>


            <Footer
                onOpenImpressum={() => setShowImpressum(true)}
                onOpenDatenschutz={() => setShowDatenschutz(true)}
            />
            {
                showImpressum && (
                    <Impressum onClose={() => setShowImpressum(false)} />
                )
            }

            {
                showDatenschutz && (
                    <Datenschutz onClose={() => setShowDatenschutz(false)} />
                )
            }
        </div>
    );

}

