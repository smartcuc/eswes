export default function EnergyFlow() {
    return (
        <div className="bg-white rounded-2xl shadow p-8 max-w-3xl mx-auto mt-10">

            <h2 className="text-xl font-semibold mb-6 text-center">
                Energie fließt gerade
            </h2>

            <div className="flex items-center justify-between">

                {/* FROM */}
                <div className="text-center">
                    <div className="w-16 h-16 bg-orange-400 rounded-full flex items-center justify-center text-white text-xl animate-pulse">
                        ☀️
                    </div>
                    <p className="mt-2 text-sm text-gray-600">Müller</p>
                </div>

                {/* FLOW LINE */}
                <div className="flex-1 mx-4 relative">

                    {/* Linie */}
                    <div className="h-1 bg-gray-200 w-full rounded"></div>

                    {/* bewegter Punkt */}
                    <div className="absolute top-1/2 -translate-y-1/2 w-4 h-4 bg-orange-500 rounded-full animate-flow"></div>

                </div>

                {/* TO */}
                <div className="text-center">
                    <div className="w-16 h-16 bg-indigo-500 rounded-full flex items-center justify-center text-white text-xl">
                        🔌
                    </div>
                    <p className="mt-2 text-sm text-gray-600">Schmidt</p>
                </div>

            </div>

        </div>
    );
}
