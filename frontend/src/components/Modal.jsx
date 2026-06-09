/*
# src/components/Modal.jsx
*/

export default function Modal({ title, children, onClose }) {
    return (
        <div className="fixed inset-0 bg-black/30 backdrop-blur-sm flex items-center justify-center z-50">

            <div className="bg-gray-50 border border-gray-200 rounded-xl shadow-xl w-full max-w-2xl p-6 relative">

                {/* Header */}
                <div className="flex justify-between items-center mb-6">
                    <h2 className="text-lg font-semibold text-indigo-600">
                        {title}
                    </h2>

                    <button
                        onClick={onClose}
                        className="text-gray-400 hover:text-black text-xl"
                    >
                        ✕
                    </button>
                </div>

                {/* Content */}
                <div className="text-gray-700 text-sm leading-relaxed max-h-[70vh] overflow-y-auto">
                    {children}
                </div>

            </div>

        </div>
    );
}

