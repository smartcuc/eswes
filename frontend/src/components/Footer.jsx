/*
# src/components/Footer.jsx
*/

export default function Footer({ onOpenImpressum, onOpenDatenschutz }) {
    return (
        <footer className="bg-gray-900 text-gray-300 mt-16 px-6 py-12">

            <div className="max-w-6xl mx-auto grid md:grid-cols-3 gap-8">

                {/* BRAND */}
                <div>

                    <h3 className="text-white font-semibold mb-2 text-lg">
                        Sharegy
                    </h3>

                    <p className="text-sm text-gray-400 leading-relaxed">
                        Die Plattform für Energy Sharing Communities.<br />
                        Energie teilen. Verstehen. Optimieren.
                    </p>

                    <p className="text-xs mt-4 text-gray-500">
                        Ein Produkt der{" "}
                        <a
                            href="https://www.smartevo.de"
                            target="_blank"
                            className="text-white hover:underline"
                        >
                            smartEvo GmbH
                        </a>
                    </p>
                </div>

                {/* LINKS */}
                <div>
                    <h4 className="text-white mb-3 font-medium">Rechtliches</h4>

                    <ul className="space-y-2 text-sm">
                        <li>
                            <button
                                onClick={onOpenImpressum}
                                className="hover:text-white"
                            >
                                Impressum
                            </button>
                        </li>
                        <li>
                            <button
                                onClick={onOpenDatenschutz}
                                className="hover:text-white"
                            >
                                Datenschutz
                            </button>
                        </li>
                    </ul>
                </div>

                {/* INFO */}
                <div>
                    <h4 className="text-white mb-3 font-medium">Info</h4>

                    <p className="text-sm text-gray-400">
                        Diese Plattform wird zur Visualisierung von Energieflüssen
                        und zur Unterstützung von Energy Sharing Communities verwendet.
                    </p>

                    <p className="text-xs mt-4 text-gray-500">
                        Teile dieser Anwendung wurden mit Unterstützung von KI-Systemen entwickelt.
                    </p>
                </div>

            </div>

            {/* COPYRIGHT */}
            <div className="text-center text-xs text-gray-500 mt-10">
                © {new Date().getFullYear()} smartEvo GmbH – Alle Rechte vorbehalten
            </div>

        </footer>
    );
}
