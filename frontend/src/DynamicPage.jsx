/*
#  DynamicPage.jsx
*/

import { useEffect, useState } from "react";
import Header from "./Header";
import Sidebar from "./Sidebar";
import BlockRenderer from "./BlockRenderer";

export default function DynamicPage({ tenantSlug, pageSlug }) {

    const [data, setData] = useState(null);

    useEffect(() => {
        fetch(`/api/public/${tenantSlug}/${pageSlug}`)
            .then(res => res.json())
            .then(setData);
    }, [tenantSlug, pageSlug]);

    if (!data) return <div>Loading...</div>;

    return (
        <div className="flex min-h-screen bg-gray-50">

            {/* ✅ Sidebar jetzt theme-aware */}
            <Sidebar theme={data.theme} />

            <div className="flex-1">

                {/* ✅ Header bekommt theme */}
                <Header theme={data.theme} />

                {/* ✅ Blocks statt JSON */}
                <div className="p-10 space-y-10">
                    {data.blocks.map(block => (
                        <BlockRenderer
                            key={block.id}
                            block={block}
                            theme={data.theme}
                        />
                    ))}

                </div>

            </div>
        </div>
    );
}

