/*
# SankeyDemo.jsx
*/

import { Sankey, Tooltip } from "recharts";

export default function SankeyDemo({ theme }) {

    const data = {
        nodes: [
            { name: "Solar" },
            { name: "Netz" },
            { name: "Haushalt" },
            { name: "Batterie" },
        ],
        links: [
            { source: 0, target: 2, value: 7 }, // Solar → Haushalt
            { source: 0, target: 3, value: 3 }, // Solar → Batterie
            { source: 1, target: 2, value: 4 }, // Netz → Haushalt
        ],
    };

    return (
        <div className="max-w-5xl mx-auto bg-white p-8 rounded-xl shadow">

            <h3 className="text-xl font-bold mb-6 text-center">
                Energiefluss (Demo)
            </h3>

            <Sankey
                width={700}
                height={300}
                data={data}
                nodePadding={30}
                margin={{ top: 20, bottom: 20 }}
                linkCurvature={0.5}
                node={{ fill: theme?.primary }}
            >
                <Tooltip />
            </Sankey>

        </div>
    );
}
