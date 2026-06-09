/*
# BlockRenderer.jsx
*/

import SankeyDemo from "./SankeyDemo";
import EnergyFlow from "./components/EnergyFlow";
import UserEnergyPanel from "./components/UserEnergyPanel";


export default function BlockRenderer({ block, theme }) {

    const primary = theme?.primary || "#f97316";
    const secondary = theme?.secondary || "#7c3aed";
    const buttonColor = theme?.button || "#000000";

    switch (block.block_type) {

        /* =========================================================
           HERO BLOCK (🔥 Hauptbereich)
        ========================================================= */
        case "hero":
            return (
                <div
                    className="py-28 text-center text-white"
                    style={{
                        background: `linear-gradient(135deg, ${primary}, ${secondary})`
                    }}
                >
                    <div className="max-w-4xl mx-auto px-6">

                        <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
                            {block.content.title}
                        </h1>

                        <p className="text-xl md:text-2xl opacity-90 mb-10">
                            {block.content.subtitle}
                        </p>

                        {/* CTA direkt im Hero */}
                        <button
                            className="px-10 py-4 rounded-xl font-semibold shadow-lg transition hover:scale-105 hover:shadow-2xl"
                            style={{
                                backgroundColor: buttonColor,
                                color: "white"
                            }}
                        >
                            Jetzt starten
                        </button>

                    </div>
                </div>
            );

        /* =========================================================
           TEXT BLOCK
        ========================================================= */
        case "text":
            return (
                <div className="max-w-3xl mx-auto py-8 px-6 text-gray-700 text-lg leading-relaxed">
                    {block.content.body}
                </div>
            );

        /* =========================================================
           CTA BLOCK (🔥 eigener CTA Bereich)
        ========================================================= */
        case "cta":
            return (
                <div className="text-center py-16">

                    <button
                        className="px-10 py-4 rounded-xl text-white shadow-lg transition hover:scale-105 hover:shadow-2xl"
                        style={{
                            background: `linear-gradient(to right, ${primary}, ${secondary})`
                        }}
                        onClick={() => {
                            if (block.content.link && block.content.link !== "#") {
                                window.location.href = block.content.link;
                            }
                        }}
                    >
                        {block.content.text}
                    </button>

                </div>
            );

        /* =========================================================
           SanKey BLOCK 
        ========================================================= */
        case "sankey":
            return (
                <div className="py-16">
                    <SankeyDemo theme={theme} />
                </div>
            );

        case "energy_flow":
            return <EnergyFlow data={block.content} />;

        case "user_energy":
            return <UserEnergyPanel />

        /* =========================================================
           DEFAULT (falls unbekannter Block)
        ========================================================= */
        default:
            return null;
    }
}
